"""
Кастомная пагинация для API.

Всегда возвращает объект пагинации с полями count, next, previous, results.
Если параметры limit/offset не указаны - возвращает все записи в поле results.
"""
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
from django.conf import settings
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class OptionalLimitOffsetPagination(LimitOffsetPagination):
    """
    Пагинация LimitOffset с консистентным форматом ответа.
    
    Всегда возвращает объект пагинации с полями: count, next, previous, results.
    Если limit или offset не указаны в запросе - возвращает все записи в results.
    Если указаны - применяет стандартную пагинацию.
    
    Примеры:
    - GET /api/cities/ -> {count: N, next: null, previous: null, results: [...все города...]}
    - GET /api/cities/?limit=10 -> {count: N, next: "...", previous: null, results: [...10 городов...]}
    - GET /api/cities/?limit=10&offset=20 -> {count: N, next: "...", previous: "...", results: [...города 21-30...]}
    """
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 100
    default_limit = None  # Отключаем дефолтный limit
    
    def get_limit(self, request):
        """
        Возвращает limit только если он явно указан в запросе.
        Если не указан - возвращает None (без пагинации).
        """
        if self.limit_query_param:
            try:
                limit = int(request.query_params[self.limit_query_param])
                # Проверяем max_limit
                if self.max_limit and limit > self.max_limit:
                    return self.max_limit
                return limit
            except (KeyError, ValueError):
                pass
        return None
    
    def get_offset(self, request):
        """
        Возвращает offset только если он явно указан в запросе.
        Если не указан - возвращает None.
        """
        if self.offset_query_param:
            try:
                return int(request.query_params[self.offset_query_param])
            except (KeyError, ValueError):
                pass
        return None
    
    def paginate_queryset(self, queryset, request, view=None):
        """
        Пагинирует queryset. Всегда возвращает список для консистентного формата.
        Если параметры не указаны - возвращает все записи.
        """
        # Получаем параметры из запроса
        limit = self.get_limit(request)
        offset = self.get_offset(request)
        
        # Сохраняем параметры в self для использования в других методах
        self.request = request
        
        # Подсчитываем общее количество записей
        self.count = self.get_count(queryset)
        
        # Если параметры не указаны - возвращаем все записи
        if limit is None and offset is None:
            self.limit = None  # Нет лимита
            self.offset = 0
            return list(queryset)
        
        # Если указан только offset без limit - устанавливаем дефолтный limit
        if limit is None and offset is not None:
            limit = 20  # Дефолтный limit если указан только offset
        
        # Если указан только limit без offset - offset = 0
        if offset is None:
            offset = 0
        
        self.limit = limit
        self.offset = offset
        
        # Проверяем границы
        if self.count == 0 or offset > self.count:
            return []
        
        # Применяем пагинацию
        if self.count > limit and self.template is not None:
            self.display_page_controls = True
        
        return list(queryset[offset:offset + limit])
    
    def get_next_link(self):
        """Переопределяем для использования правильного хоста"""
        # Вычисляем has_next самостоятельно
        if self.limit is None:
            return None
        
        has_next = (self.offset + self.limit) < self.count
        if not has_next:
            return None
        
        url = self.request.build_absolute_uri()
        # Заменяем хост на правильный в зависимости от окружения
        url = self._fix_url_host(url)
        
        offset = self.offset + self.limit
        return self._replace_query_param(url, self.offset_query_param, offset)
    
    def get_previous_link(self):
        """Переопределяем для использования правильного хоста"""
        # Вычисляем has_previous самостоятельно
        if self.limit is None:
            return None
        
        has_previous = self.offset > 0
        if not has_previous:
            return None
        
        url = self.request.build_absolute_uri()
        # Заменяем хост на правильный в зависимости от окружения
        url = self._fix_url_host(url)
        
        if self.offset - self.limit <= 0:
            url = self._remove_query_param(url, self.offset_query_param)
            return self._replace_query_param(url, self.limit_query_param, self.limit)
        
        offset = self.offset - self.limit
        return self._replace_query_param(url, self.offset_query_param, offset)
    
    def _replace_query_param(self, url, key, value):
        """
        Заменяет или добавляет query параметр в URL.
        """
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        query_params[key] = [str(value)]
        new_query = urlencode(query_params, doseq=True)
        new_parsed = parsed._replace(query=new_query)
        return urlunparse(new_parsed)
    
    def _remove_query_param(self, url, key):
        """
        Удаляет query параметр из URL.
        """
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        query_params.pop(key, None)
        new_query = urlencode(query_params, doseq=True)
        new_parsed = parsed._replace(query=new_query)
        return urlunparse(new_parsed)
    
    def _fix_url_host(self, url):
        """
        Исправляет хост в URL в зависимости от окружения.
        В dev использует localhost:8001 (порт из docker-compose.dev.yml), 
        в prod использует настройку из переменных окружения.
        """
        import re
        
        # В dev окружении всегда используем localhost:8001
        if settings.DEBUG:
            # Заменяем любой хост (http или https) на http://localhost:8001 для dev
            # Порт 8001 - это внешний порт из docker-compose.dev.yml
            url = re.sub(r'https?://[^/]+', 'http://localhost:8001', url)
            return url
        
        # В prod используем хост из переменных окружения, если указан
        api_host = getattr(settings, 'API_HOST', None)
        if api_host:
            # Определяем протокол (http или https) из оригинального URL
            protocol = 'https' if url.startswith('https://') else 'http'
            # Заменяем хост на указанный в настройках
            url = re.sub(r'https?://[^/]+', f'{protocol}://{api_host}', url)
        
        return url
    
    def get_paginated_response(self, data):
        """
        Всегда возвращает ответ с метаданными пагинации.
        """
        # Если limit не был установлен (все записи), next и previous всегда null
        if self.limit is None:
            return Response({
                'count': self.count,
                'next': None,
                'previous': None,
                'results': data
            })
        
        # Стандартная пагинация с next/previous ссылками
        return Response({
            'count': self.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

