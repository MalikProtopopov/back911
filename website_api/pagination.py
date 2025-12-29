"""
Кастомная пагинация для API.

Всегда возвращает объект пагинации с полями count, next, previous, results.
Если параметры limit/offset не указаны - возвращает все записи в поле results.
"""
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

