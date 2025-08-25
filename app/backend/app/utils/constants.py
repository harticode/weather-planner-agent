SUNNY_CODES = {0, 1, 2}  # Codes for sunny weather conditions

_ACTIVITY_PREFS = {
    'beach': {
        'min_temp_c': 24, 'need_sun': True, 'max_precip': 20, 'max_wind_kmh': 35,
        'duration_hours': 4, 'best_time_range': (10, 16),
        'indoor_alternative': 'Visit aquarium or spa'
    },
    'hiking': {
        'min_temp_c': 12, 'need_sun': False, 'max_precip': 30, 'max_wind_kmh': 45,
        'duration_hours': 3, 'best_time_range': (8, 17),
        'indoor_alternative': 'Indoor rock climbing or gym workout'
    },
    'picnic': {
        'min_temp_c': 18, 'need_sun': False, 'max_precip': 30, 'max_wind_kmh': 35,
        'duration_hours': 2, 'best_time_range': (11, 15),
        'indoor_alternative': 'Indoor food court or restaurant with outdoor seating'
    },
    'cycling': {
        'min_temp_c': 14, 'need_sun': False, 'max_precip': 25, 'max_wind_kmh': 35,
        'duration_hours': 2, 'best_time_range': (7, 18),
        'indoor_alternative': 'Stationary cycling or spin class'
    },
    'swimming': {
        'min_temp_c': 22, 'need_sun': False, 'max_precip': 25, 'max_wind_kmh': 35,
        'duration_hours': 1.5, 'best_time_range': (9, 19),
        'indoor_alternative': 'Indoor pool or spa'
    },
    'kayaking': {
        'min_temp_c': 18, 'need_sun': False, 'max_precip': 25, 'max_wind_kmh': 30,
        'duration_hours': 3, 'best_time_range': (9, 17),
        'indoor_alternative': 'Indoor rowing or water sports center'
    },
    'running': {
        'min_temp_c': 8, 'need_sun': False, 'max_precip': 40, 'max_wind_kmh': 40,
        'duration_hours': 1, 'best_time_range': (6, 20),
        'indoor_alternative': 'Treadmill running or indoor track'
    },
    'tennis': {
        'min_temp_c': 15, 'need_sun': False, 'max_precip': 20, 'max_wind_kmh': 30,
        'duration_hours': 2, 'best_time_range': (8, 19),
        'indoor_alternative': 'Indoor tennis court'
    },
    'golf': {
        'min_temp_c': 12, 'need_sun': False, 'max_precip': 20, 'max_wind_kmh': 40,
        'duration_hours': 4, 'best_time_range': (7, 17),
        'indoor_alternative': 'Driving range or golf simulator'
    },
    'fishing': {
        'min_temp_c': 10, 'need_sun': False, 'max_precip': 35, 'max_wind_kmh': 25,
        'duration_hours': 4, 'best_time_range': (6, 18),
        'indoor_alternative': 'Visit aquarium or fishing equipment store'
    },
    'photography': {
        'min_temp_c': 5, 'need_sun': False, 'max_precip': 45, 'max_wind_kmh': 50,
        'duration_hours': 3, 'best_time_range': (7, 19),
        'indoor_alternative': 'Indoor photography (museums, architecture, portraits)'
    },
    'gardening': {
        'min_temp_c': 10, 'need_sun': False, 'max_precip': 20, 'max_wind_kmh': 30,
        'duration_hours': 2, 'best_time_range': (8, 17),
        'indoor_alternative': 'Indoor plant care or visit garden center'
    },
    'bbq': {
        'min_temp_c': 16, 'need_sun': False, 'max_precip': 15, 'max_wind_kmh': 25,
        'duration_hours': 3, 'best_time_range': (11, 20),
        'indoor_alternative': 'Indoor grilling or cooking class'
    },
    'festivals': {
        'min_temp_c': 12, 'need_sun': False, 'max_precip': 30, 'max_wind_kmh': 40,
        'duration_hours': 6, 'best_time_range': (10, 22),
        'indoor_alternative': 'Indoor concerts or cultural events'
    },
    'camping': {
        'min_temp_c': 8, 'need_sun': False, 'max_precip': 25, 'max_wind_kmh': 35,
        'duration_hours': 24, 'best_time_range': (14, 18),
        'indoor_alternative': 'Glamping or cabin rental'
    },
    'skateboarding': {
        'min_temp_c': 10, 'need_sun': False, 'max_precip': 10, 'max_wind_kmh': 30,
        'duration_hours': 2, 'best_time_range': (9, 19),
        'indoor_alternative': 'Indoor skate park'
    },
    'stargazing': {
        'min_temp_c': 5, 'need_sun': False, 'max_precip': 10, 'max_wind_kmh': 20,
        'duration_hours': 3, 'best_time_range': (20, 2),
        'indoor_alternative': 'Planetarium visit'
    },
    'skiing': {
        'min_temp_c': -5, 'need_sun': False, 'max_precip': 80, 'max_wind_kmh': 50,
        'duration_hours': 6, 'best_time_range': (9, 16),
        'indoor_alternative': 'Indoor ski simulator'
    },
    'surfing': {
        'min_temp_c': 18, 'need_sun': False, 'max_precip': 40, 'max_wind_kmh': 25,
        'duration_hours': 3, 'best_time_range': (7, 17),
        'indoor_alternative': 'Indoor surfing or wave pool'
    },
    'kite_flying': {
        'min_temp_c': 8, 'need_sun': False, 'max_precip': 20, 'max_wind_kmh': 45,
        'min_wind_kmh': 15,
        'duration_hours': 2, 'best_time_range': (10, 17),
        'indoor_alternative': 'Indoor kite making workshop'
    },
    'outdoor_dining': {
        'min_temp_c': 16, 'need_sun': False, 'max_precip': 15, 'max_wind_kmh': 25,
        'duration_hours': 2, 'best_time_range': (12, 21),
        'indoor_alternative': 'Restaurant with covered terrace'
    }
}
