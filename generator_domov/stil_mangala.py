# -*- coding: utf-8 -*-
"""Правила облика Мангалы для генератора — числа из ответа Астры 28.09 (`OTVET-ASTRY-GENERATOR-DOMOV-2026-09-28.md`),
семейства — по её ответу на анкету 27.09 (`OTVET-ASTRY-YANTRY-I-OBLIK-SEL-2026-09-27.md`) и программам комнат разведки
(`zamysel/art/oblik-sel/opyt-dom-s-nutrom/razvedka-nutro/razvedka-programmy-komnat.md`). Это стартовые параметры
пробы, не строительные нормативы: зерно выбирает внутри диапазонов, связи конструкции и три признака семейства —
всегда.

С 30 м Мангала узнаётся по трём признакам: красное каменное основание, уступчатый силуэт, глубокая тень защищённого
входа.
"""

# места материалов — те же номера, что у `ue/dom_detali.py` и пусковых домов набора (SLOTY): 0 камень, 1 известь,
# 2 тёмный брус, 3 черепица, 4 стекло, 5 мареновая ткань/краска, 6 железо, 7 травы, 8 цветы, 9 доски, 10 ткань-мешки,
# 11 мощение (плиты пола, ступени), 12 угли (светятся: огонь очага и горна — на углях, не на стенах; Астра 28.09)
KAM, SHT, BRUS, CHER, STEK, KRAS, ZHEL, TRAV, CVET, DOSKI, TKAN, MOSH, UGLI = range(13)

STIL = {
    'zemlya': 'mangala',
    # фасад
    'cokol': (0.45, 0.9),              # высота красного цоколя, м; на склоне до 1,5
    'cokol_sklon': 1.5,
    'okno_shir': (0.65, 0.95),
    'okno_vys': (1.0, 1.35),
    'prostenok': (0.8, 1.5),
    'otkos': (0.15, 0.25),             # глубина откоса окна
    'svs': (0.55, 0.85),               # свес кровли
    'vypusk_balok': (0.15, 0.30),      # вынос концов балок
    'stavni_dolya': 0.75,              # ставни — основной вариант у жилья; решётки — кладовые и мастерские
    # стены
    'stena_nar': 0.5,                  # наружная стена (камень внизу, известь выше)
    'stena_vn': 0.18,                  # перегородка
    'etazh_niz': 3.1,                  # высота низа в свету
    'etazh_verh': 2.8,
    'perekrytie': 0.3,
    # нутро
    'dver_vhod': (1.2, 1.6),           # ширина входной двери
    'dver_vn': (0.9, 1.1),
    'prohod': (1.2, 1.5),              # проход лестницы и коридора
    'nad_golovoj': 2.2,
    'lestnica_ugol': 34.0,             # не круче 38°; ступень ≤ 0,19, проступь ≥ 0,27 (разведка 28.09, проверено в 5.8)
    'dver_vys': 2.35,                  # двери 1,0–1,2 × 2,35 м; навигация: радиус агента 0,34, шаг 0,35, уклон 44°
    'predmetov_na_komnatu': (8, 15),
    # против ровности
    'kamni_razmerov': (3, 5),
    'kamen_vystup': (0.01, 0.03),
    'kraj_shtukaturki': (0.02, 0.05),
    'doski_raznica': (0.10, 0.15),
    'konek_provis': (0.02, 0.04),      # на 6 м, иногда
    'povrezhdeno_maks': 0.05,
    # акцент
    'tkan_kazhdyj': 4,                 # мареновая ткань — примерно у каждого четвёртого жилого дома
}

# семейства: этажи, основной корпус (без двора и навесов), кровля и уклон, вход, программа комнат по этажам
# (площади в свету, м²; 'gl' — главный предмет комнаты), нутро по квоте
SEMEJSTVA = {
    'm-traktir-masterskaya': {
        'etazhi': 2, 'korpus_u': (10.0, 13.0), 'korpus_v': (8.0, 10.0),
        'krysha': 'valmovaya', 'uklon': (22.0, 30.0),
        'vhod': 'galereya_uglovaya', 'galereya_glub': (2.0, 3.0), 'dvor': 'sboku',
        'tri_podema': True,            # единственный узел «трёх подъёмов» в селе
        'kompozicii': ('naves', 'galereya', 'ugol', 'pristrojka'),   # Астра 28.09: крупно различающиеся варианты
        'kuznya_naves': True,
        'etazh': [
            [('zal', 'общий зал', 40.0, 'ochag'), ('povarnya', 'поварня', 9.0, 'pech'),
             ('kladovaya', 'кладовая', 8.0, 'zakroma')],
            [('koridor', 'коридор', 10.0, None), ('gostevaya', 'гостевая', 8.0, 'krovat'),
             ('gostevaya', 'гостевая', 8.0, 'krovat'), ('nochlezhka', 'ночлежка', 12.0, 'nary'),
             ('hozyajskaya', 'хозяйская', 10.0, 'krovat')],
        ],
        'nutro': 'polnoe',
    },
    'm-kuznya': {
        'etazhi': 1, 'korpus_u': (6.0, 8.0), 'korpus_v': (5.0, 7.0),
        'krysha': 'odnoskatnaya', 'uklon': (15.0, 22.0),
        'vhod': 'naves_rabochij', 'naves_glub': (3.0, 4.0), 'dvor': 'szadi',
        'etazh': [[('masterskaya', 'мастерская', 28.0, 'verstak'), ('sklad', 'склад', 6.0, 'zakroma')]],
        'nutro': 'chastichnoe',
    },
    'm-dom-dvor': {
        'etazhi': 1, 'korpus_u': (6.0, 9.0), 'korpus_v': (5.0, 7.0),
        'krysha': 'ploskaya', 'uklon': (2.0, 4.0), 'parapet': True,
        'vhod': 'nisha', 'nisha_glub': (0.6, 1.0), 'dvor': 'sboku',
        'etazh': [[('gornica', 'общая комната', 22.0, 'ochag'), ('spalnya', 'спальня', 11.0, 'krovat'),
                   ('kladovaya', 'кладовая', 4.0, 'zakroma')]],
        'nutro': 'po_kvote',
    },
    'm-dom-sklon': {
        'etazhi': 2, 'korpus_u': (7.0, 9.0), 'korpus_v': (6.0, 8.0),
        'krysha': 'dvuskatnaya', 'uklon': (22.0, 30.0),
        'vhod': 'galereya_lestnica', 'dvor': 'vdol_sklona',
        'etazh': [[('stojlo', 'стойло', 22.0, 'yasli'), ('pogreb', 'кладовая-погреб', 14.0, 'zakroma')],
                  [('gornica', 'общая комната', 24.0, 'ochag'), ('spalnya', 'спальня', 11.0, 'krovat'),
                   ('spalnya', 'спальня', 10.0, 'krovat')]],
        'nutro': 'po_kvote',
    },
    'm-saraj': {
        'etazhi': 1, 'korpus_u': (4.0, 6.0), 'korpus_v': (3.0, 5.0),
        'krysha': 'odnoskatnaya', 'uklon': (12.0, 18.0),
        'vhod': 'vorota', 'dvor': 'v_glubine',
        'etazh': [[('saraj', 'сарай', 14.0, 'zakroma')]],
        'nutro': 'gluhoe',
    },
}

# чего генератор не делает никогда (Астра, п. 6) — проверяется в proverki.py
NIKOGDA = [
    'все дома — уменьшенная копия трактира',
    'случайный перекос стен, лестниц, опор ради «живости»',
    'оранжевый свет, запечённый в цвет стен',
    'балка поперёк окна; труба без очага; лестница в закрытый потолок',
    'реквизит и зелень вместо архитектуры',
]
