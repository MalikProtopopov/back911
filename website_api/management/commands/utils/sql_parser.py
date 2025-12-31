"""SQL dump parser utility"""
import re
from typing import List, Dict, Tuple, Optional


def parse_cities(dump_path: str) -> List[Dict[str, any]]:
    """
    Parse cities from SQL dump.
    
    Returns list of dicts: [{'id': 8, 'title': 'Ижевск'}, ...]
    """
    cities = []
    
    with open(dump_path, 'r', encoding='utf-8') as f:
        in_city_section = False
        
        for line in f:
            # Start of city data
            if 'COPY public.city_db' in line and 'FROM stdin' in line:
                in_city_section = True
                continue
            
            # End of section
            if in_city_section and line.strip() == '\\.':
                break
            
            # Parse city data
            if in_city_section and line.strip():
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    try:
                        city_id = int(parts[0])
                        title = parts[1]
                        cities.append({
                            'id': city_id,
                            'title': title
                        })
                    except ValueError:
                        continue
    
    return cities


def parse_services(dump_path: str) -> List[Dict[str, any]]:
    """
    Parse services from SQL dump.
    
    Returns list of dicts: [{'id': 1, 'title': 'Выездной шиномонтаж'}, ...]
    """
    services = []
    
    with open(dump_path, 'r', encoding='utf-8') as f:
        in_service_section = False
        
        for line in f:
            if 'COPY public.service_db' in line and 'FROM stdin' in line:
                in_service_section = True
                continue
            
            if in_service_section and line.strip() == '\\.':
                break
            
            if in_service_section and line.strip():
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    try:
                        service_id = int(parts[0])
                        title = parts[1]
                        services.append({
                            'id': service_id,
                            'title': title
                        })
                    except ValueError:
                        continue
    
    return services


def parse_technic_categories(dump_path: str) -> List[Dict[str, any]]:
    """
    Parse technic categories from SQL dump.
    
    Returns list of dicts: [{'id': 3, 'title': 'Грузовой автомобиль'}, ...]
    """
    categories = []
    
    with open(dump_path, 'r', encoding='utf-8') as f:
        in_category_section = False
        
        for line in f:
            if 'COPY public.technic_category_db' in line and 'FROM stdin' in line:
                in_category_section = True
                continue
            
            if in_category_section and line.strip() == '\\.':
                break
            
            if in_category_section and line.strip():
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    try:
                        cat_id = int(parts[0])
                        title = parts[1]
                        categories.append({
                            'id': cat_id,
                            'title': title
                        })
                    except ValueError:
                        continue
    
    return categories


def parse_options(dump_path: str) -> List[Dict[str, any]]:
    """
    Parse options from SQL dump.
    
    Returns list of dicts: [{'id': 3, 'title': 'Зарядка аккумулятора', 'service_id': 1}, ...]
    """
    options = []
    
    with open(dump_path, 'r', encoding='utf-8') as f:
        in_option_section = False
        
        for line in f:
            if 'COPY public.option_db' in line and 'FROM stdin' in line:
                in_option_section = True
                continue
            
            if in_option_section and line.strip() == '\\.':
                break
            
            if in_option_section and line.strip():
                parts = line.strip().split('\t')
                if len(parts) >= 3:
                    try:
                        option_id = int(parts[0])
                        title = parts[1]
                        service_id = int(parts[2])
                        options.append({
                            'id': option_id,
                            'title': title,
                            'service_id': service_id
                        })
                    except ValueError:
                        continue
    
    return options


def parse_prices(dump_path: str) -> List[Dict[str, any]]:
    """
    Parse option prices from SQL dump.
    
    Returns list of dicts: [{
        'id': 61,
        'amount': '1500.00',
        'city_id': 3,
        'option_id': 18,
        'technic_category_id': 3 or None
    }, ...]
    """
    prices = []
    
    with open(dump_path, 'r', encoding='utf-8') as f:
        in_price_section = False
        
        for line in f:
            if 'COPY public.option_price_db' in line and 'FROM stdin' in line:
                in_price_section = True
                continue
            
            if in_price_section and line.strip() == '\\.':
                break
            
            if in_price_section and line.strip():
                parts = line.strip().split('\t')
                if len(parts) >= 5:
                    try:
                        price_id = int(parts[0])
                        amount = parts[1]
                        city_id = int(parts[2])
                        option_id = int(parts[3])
                        technic_cat_id = None if parts[4] == '\\N' else int(parts[4])
                        
                        prices.append({
                            'id': price_id,
                            'amount': amount,
                            'city_id': city_id,
                            'option_id': option_id,
                            'technic_category_id': technic_cat_id
                        })
                    except (ValueError, IndexError):
                        continue
    
    return prices


def parse_order_conditions(dump_path: str) -> List[Dict[str, any]]:
    """
    Parse order conditions (parameters) from SQL dump.
    
    Returns list of dicts: [{
        'id': 965,
        'title': '13',  # Значение параметра (R13, АИ-92...)
        'condition_type': 'radius',  # Тип параметра
        'additional_price': '1500.00',  # Цена/надбавка
        'option_id': 4588 or None  # Связь с опцией
    }, ...]
    """
    conditions = []
    
    with open(dump_path, 'r', encoding='utf-8') as f:
        in_condition_section = False
        
        for line in f:
            if 'COPY public.order_condition_db' in line and 'FROM stdin' in line:
                in_condition_section = True
                continue
            
            if in_condition_section and line.strip() == '\\.':
                break
            
            if in_condition_section and line.strip():
                parts = line.strip().split('\t')
                if len(parts) >= 5:
                    try:
                        condition_id = int(parts[0])
                        title = parts[1]
                        condition_type = parts[2]
                        additional_price = parts[3]
                        option_id = None if parts[4] == '\\N' else int(parts[4])
                        
                        conditions.append({
                            'id': condition_id,
                            'title': title,
                            'condition_type': condition_type,
                            'additional_price': additional_price,
                            'option_id': option_id
                        })
                    except (ValueError, IndexError):
                        continue
    
    return conditions


def parse_working_zones(dump_path: str) -> List[Dict[str, any]]:
    """
    Parse working zones (delivery zones) from SQL dump.
    
    Returns list of dicts: [{
        'id': 30,
        'title': 'Воронеж - внешняя',
        'area_coordinates': '[[39.307584, 51.777745], ...]',  # JSON string
        'departure_price': '2000.00',
        'location_status': 'out_city' or 'in_city' or None,
        'city_id': 4 or None
    }, ...]
    """
    zones = []
    
    with open(dump_path, 'r', encoding='utf-8') as f:
        in_zone_section = False
        
        for line in f:
            if 'COPY public.working_zone_db' in line and 'FROM stdin' in line:
                in_zone_section = True
                continue
            
            if in_zone_section and line.strip() == '\\.':
                break
            
            if in_zone_section and line.strip():
                parts = line.strip().split('\t')
                if len(parts) >= 6:
                    try:
                        zone_id = int(parts[0])
                        title = parts[1]
                        area_coordinates = parts[2]
                        departure_price = parts[3]
                        location_status = None if parts[4] == '\\N' else parts[4]
                        city_id = None if parts[5] == '\\N' else int(parts[5])
                        
                        zones.append({
                            'id': zone_id,
                            'title': title,
                            'area_coordinates': area_coordinates,
                            'departure_price': departure_price,
                            'location_status': location_status,
                            'city_id': city_id
                        })
                    except (ValueError, IndexError):
                        continue
    
    return zones


def transliterate(text: str) -> str:
    """
    Transliterate Russian text to Latin for slug generation.
    """
    translit_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
        'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
        'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
        'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
        'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch',
        'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '',
        'э': 'e', 'ю': 'yu', 'я': 'ya',
    }
    
    text = text.lower()
    result = []
    
    for char in text:
        if char in translit_map:
            result.append(translit_map[char])
        elif char.isalnum() or char in ['-', '_']:
            result.append(char)
        elif char == ' ':
            result.append('-')
    
    # Clean up multiple dashes
    slug = ''.join(result)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    
    return slug

