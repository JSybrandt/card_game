from typing import Tuple

# Take a look here for all the colors:
# https://material.io/resources/color/#!/

Color = Tuple[int, int, int]


def assert_valid_color(color: Color):
  assert len(color) == 3, f"Invalid color: {color}"
  assert 0 <= color[0] <= 255, f"Invalid color: {color}"
  assert 0 <= color[1] <= 255, f"Invalid color: {color}"
  assert 0 <= color[2] <= 255, f"Invalid color: {color}"


RED = 0xF4, 0x43, 0x36
RED_50 = 0xFF, 0xEB, 0xEE
RED_100 = 0xFF, 0xCD, 0xD2
RED_200 = 0xEF, 0x9A, 0x9A
RED_300 = 0xE5, 0x73, 0x73
RED_400 = 0xEF, 0x53, 0x50
RED_500 = 0xF4, 0x43, 0x36
RED_600 = 0xE5, 0x39, 0x35
RED_700 = 0xD3, 0x2F, 0x2F
RED_800 = 0xC6, 0x28, 0x28
RED_900 = 0xB7, 0x1C, 0x1C
RED_A100 = 0xFF, 0x8A, 0x80
RED_A200 = 0xFF, 0x52, 0x52
RED_A400 = 0xFF, 0x17, 0x44
RED_A700 = 0xD5, 0x00, 0x00
PINK = 0xE9, 0x1E, 0x63
PINK_50 = 0xFC, 0xE4, 0xEC
PINK_100 = 0xF8, 0xBB, 0xD0
PINK_200 = 0xF4, 0x8F, 0xB1
PINK_300 = 0xF0, 0x62, 0x92
PINK_400 = 0xEC, 0x40, 0x7A
PINK_500 = 0xE9, 0x1E, 0x63
PINK_600 = 0xD8, 0x1B, 0x60
PINK_700 = 0xC2, 0x18, 0x5B
PINK_800 = 0xAD, 0x14, 0x57
PINK_900 = 0x88, 0x0E, 0x4F
PINK_A100 = 0xFF, 0x80, 0xAB
PINK_A200 = 0xFF, 0x40, 0x81
PINK_A400 = 0xF5, 0x00, 0x57
PINK_A700 = 0xC5, 0x11, 0x62
PURPLE = 0x9C, 0x27, 0xB0
PURPLE_50 = 0xF3, 0xE5, 0xF5
PURPLE_100 = 0xE1, 0xBE, 0xE7
PURPLE_200 = 0xCE, 0x93, 0xD8
PURPLE_300 = 0xBA, 0x68, 0xC8
PURPLE_400 = 0xAB, 0x47, 0xBC
PURPLE_500 = 0x9C, 0x27, 0xB0
PURPLE_600 = 0x8E, 0x24, 0xAA
PURPLE_700 = 0x7B, 0x1F, 0xA2
PURPLE_800 = 0x6A, 0x1B, 0x9A
PURPLE_900 = 0x4A, 0x14, 0x8C
PURPLE_A100 = 0xEA, 0x80, 0xFC
PURPLE_A200 = 0xE0, 0x40, 0xFB
PURPLE_A400 = 0xD5, 0x00, 0xF9
PURPLE_A700 = 0xAA, 0x00, 0xFF
DEEP_PURPLE = 0x67, 0x3A, 0xB7
DEEP_PURPLE_50 = 0xED, 0xE7, 0xF6
DEEP_PURPLE_100 = 0xD1, 0xC4, 0xE9
DEEP_PURPLE_200 = 0xB3, 0x9D, 0xDB
DEEP_PURPLE_300 = 0x95, 0x75, 0xCD
DEEP_PURPLE_400 = 0x7E, 0x57, 0xC2
DEEP_PURPLE_500 = 0x67, 0x3A, 0xB7
DEEP_PURPLE_600 = 0x5E, 0x35, 0xB1
DEEP_PURPLE_700 = 0x51, 0x2D, 0xA8
DEEP_PURPLE_800 = 0x45, 0x27, 0xA0
DEEP_PURPLE_900 = 0x31, 0x1B, 0x92
DEEP_PURPLE_A100 = 0xB3, 0x88, 0xFF
DEEP_PURPLE_A200 = 0x7C, 0x4D, 0xFF
DEEP_PURPLE_A400 = 0x65, 0x1F, 0xFF
DEEP_PURPLE_A700 = 0x62, 0x00, 0xEA
INDIGO = 0x3F, 0x51, 0xB5
INDIGO_50 = 0xE8, 0xEA, 0xF6
INDIGO_100 = 0xC5, 0xCA, 0xE9
INDIGO_200 = 0x9F, 0xA8, 0xDA
INDIGO_300 = 0x79, 0x86, 0xCB
INDIGO_400 = 0x5C, 0x6B, 0xC0
INDIGO_500 = 0x3F, 0x51, 0xB5
INDIGO_600 = 0x39, 0x49, 0xAB
INDIGO_700 = 0x30, 0x3F, 0x9F
INDIGO_800 = 0x28, 0x35, 0x93
INDIGO_900 = 0x1A, 0x23, 0x7E
INDIGO_A100 = 0x8C, 0x9E, 0xFF
INDIGO_A200 = 0x53, 0x6D, 0xFE
INDIGO_A400 = 0x3D, 0x5A, 0xFE
INDIGO_A700 = 0x30, 0x4F, 0xFE
BLUE = 0x21, 0x96, 0xF3
BLUE_50 = 0xE3, 0xF2, 0xFD
BLUE_100 = 0xBB, 0xDE, 0xFB
BLUE_200 = 0x90, 0xCA, 0xF9
BLUE_300 = 0x64, 0xB5, 0xF6
BLUE_400 = 0x42, 0xA5, 0xF5
BLUE_500 = 0x21, 0x96, 0xF3
BLUE_600 = 0x1E, 0x88, 0xE5
BLUE_700 = 0x19, 0x76, 0xD2
BLUE_800 = 0x15, 0x65, 0xC0
BLUE_900 = 0x0D, 0x47, 0xA1
BLUE_A100 = 0x82, 0xB1, 0xFF
BLUE_A200 = 0x44, 0x8A, 0xFF
BLUE_A400 = 0x29, 0x79, 0xFF
BLUE_A700 = 0x29, 0x62, 0xFF
LIGHT_BLUE = 0x03, 0xA9, 0xF4
LIGHT_BLUE_50 = 0xE1, 0xF5, 0xFE
LIGHT_BLUE_100 = 0xB3, 0xE5, 0xFC
LIGHT_BLUE_200 = 0x81, 0xD4, 0xFA
LIGHT_BLUE_300 = 0x4F, 0xC3, 0xF7
LIGHT_BLUE_400 = 0x29, 0xB6, 0xF6
LIGHT_BLUE_500 = 0x03, 0xA9, 0xF4
LIGHT_BLUE_600 = 0x03, 0x9B, 0xE5
LIGHT_BLUE_700 = 0x02, 0x88, 0xD1
LIGHT_BLUE_800 = 0x02, 0x77, 0xBD
LIGHT_BLUE_900 = 0x01, 0x57, 0x9B
LIGHT_BLUE_A100 = 0x80, 0xD8, 0xFF
LIGHT_BLUE_A200 = 0x40, 0xC4, 0xFF
LIGHT_BLUE_A400 = 0x00, 0xB0, 0xFF
LIGHT_BLUE_A700 = 0x00, 0x91, 0xEA
CYAN = 0x00, 0xBC, 0xD4
CYAN_50 = 0xE0, 0xF7, 0xFA
CYAN_100 = 0xB2, 0xEB, 0xF2
CYAN_200 = 0x80, 0xDE, 0xEA
CYAN_300 = 0x4D, 0xD0, 0xE1
CYAN_400 = 0x26, 0xC6, 0xDA
CYAN_500 = 0x00, 0xBC, 0xD4
CYAN_600 = 0x00, 0xAC, 0xC1
CYAN_700 = 0x00, 0x97, 0xA7
CYAN_800 = 0x00, 0x83, 0x8F
CYAN_900 = 0x00, 0x60, 0x64
CYAN_A100 = 0x84, 0xFF, 0xFF
CYAN_A200 = 0x18, 0xFF, 0xFF
CYAN_A400 = 0x00, 0xE5, 0xFF
CYAN_A700 = 0x00, 0xB8, 0xD4
TEAL = 0x00, 0x96, 0x88
TEAL_50 = 0xE0, 0xF2, 0xF1
TEAL_100 = 0xB2, 0xDF, 0xDB
TEAL_200 = 0x80, 0xCB, 0xC4
TEAL_300 = 0x4D, 0xB6, 0xAC
TEAL_400 = 0x26, 0xA6, 0x9A
TEAL_500 = 0x00, 0x96, 0x88
TEAL_600 = 0x00, 0x89, 0x7B
TEAL_700 = 0x00, 0x79, 0x6B
TEAL_800 = 0x00, 0x69, 0x5C
TEAL_900 = 0x00, 0x4D, 0x40
TEAL_A100 = 0xA7, 0xFF, 0xEB
TEAL_A200 = 0x64, 0xFF, 0xDA
TEAL_A400 = 0x1D, 0xE9, 0xB6
TEAL_A700 = 0x00, 0xBF, 0xA5
GREEN = 0x4C, 0xAF, 0x50
GREEN_50 = 0xE8, 0xF5, 0xE9
GREEN_100 = 0xC8, 0xE6, 0xC9
GREEN_200 = 0xA5, 0xD6, 0xA7
GREEN_300 = 0x81, 0xC7, 0x84
GREEN_400 = 0x66, 0xBB, 0x6A
GREEN_500 = 0x4C, 0xAF, 0x50
GREEN_600 = 0x43, 0xA0, 0x47
GREEN_700 = 0x38, 0x8E, 0x3C
GREEN_800 = 0x2E, 0x7D, 0x32
GREEN_900 = 0x1B, 0x5E, 0x20
GREEN_A100 = 0xB9, 0xF6, 0xCA
GREEN_A200 = 0x69, 0xF0, 0xAE
GREEN_A400 = 0x00, 0xE6, 0x76
GREEN_A700 = 0x00, 0xC8, 0x53
LIGHT_GREEN = 0x8B, 0xC3, 0x4A
LIGHT_GREEN_50 = 0xF1, 0xF8, 0xE9
LIGHT_GREEN_100 = 0xDC, 0xED, 0xC8
LIGHT_GREEN_200 = 0xC5, 0xE1, 0xA5
LIGHT_GREEN_300 = 0xAE, 0xD5, 0x81
LIGHT_GREEN_400 = 0x9C, 0xCC, 0x65
LIGHT_GREEN_500 = 0x8B, 0xC3, 0x4A
LIGHT_GREEN_600 = 0x7C, 0xB3, 0x42
LIGHT_GREEN_700 = 0x68, 0x9F, 0x38
LIGHT_GREEN_800 = 0x55, 0x8B, 0x2F
LIGHT_GREEN_900 = 0x33, 0x69, 0x1E
LIGHT_GREEN_A100 = 0xCC, 0xFF, 0x90
LIGHT_GREEN_A200 = 0xB2, 0xFF, 0x59
LIGHT_GREEN_A400 = 0x76, 0xFF, 0x03
LIGHT_GREEN_A700 = 0x64, 0xDD, 0x17
LIME = 0xCD, 0xDC, 0x39
LIME_50 = 0xF9, 0xFB, 0xE7
LIME_100 = 0xF0, 0xF4, 0xC3
LIME_200 = 0xE6, 0xEE, 0x9C
LIME_300 = 0xDC, 0xE7, 0x75
LIME_400 = 0xD4, 0xE1, 0x57
LIME_500 = 0xCD, 0xDC, 0x39
LIME_600 = 0xC0, 0xCA, 0x33
LIME_700 = 0xAF, 0xB4, 0x2B
LIME_800 = 0x9E, 0x9D, 0x24
LIME_900 = 0x82, 0x77, 0x17
LIME_A100 = 0xF4, 0xFF, 0x81
LIME_A200 = 0xEE, 0xFF, 0x41
LIME_A400 = 0xC6, 0xFF, 0x00
LIME_A700 = 0xAE, 0xEA, 0x00
YELLOW = 0xFF, 0xEB, 0x3B
YELLOW_50 = 0xFF, 0xFD, 0xE7
YELLOW_100 = 0xFF, 0xF9, 0xC4
YELLOW_200 = 0xFF, 0xF5, 0x9D
YELLOW_300 = 0xFF, 0xF1, 0x76
YELLOW_400 = 0xFF, 0xEE, 0x58
YELLOW_500 = 0xFF, 0xEB, 0x3B
YELLOW_600 = 0xFD, 0xD8, 0x35
YELLOW_700 = 0xFB, 0xC0, 0x2D
YELLOW_800 = 0xF9, 0xA8, 0x25
YELLOW_900 = 0xF5, 0x7F, 0x17
YELLOW_A100 = 0xFF, 0xFF, 0x8D
YELLOW_A200 = 0xFF, 0xFF, 0x00
YELLOW_A400 = 0xFF, 0xEA, 0x00
YELLOW_A700 = 0xFF, 0xD6, 0x00
AMBER = 0xFF, 0xC1, 0x07
AMBER_50 = 0xFF, 0xF8, 0xE1
AMBER_100 = 0xFF, 0xEC, 0xB3
AMBER_200 = 0xFF, 0xE0, 0x82
AMBER_300 = 0xFF, 0xD5, 0x4F
AMBER_400 = 0xFF, 0xCA, 0x28
AMBER_500 = 0xFF, 0xC1, 0x07
AMBER_600 = 0xFF, 0xB3, 0x00
AMBER_700 = 0xFF, 0xA0, 0x00
AMBER_800 = 0xFF, 0x8F, 0x00
AMBER_900 = 0xFF, 0x6F, 0x00
AMBER_A100 = 0xFF, 0xE5, 0x7F
AMBER_A200 = 0xFF, 0xD7, 0x40
AMBER_A400 = 0xFF, 0xC4, 0x00
AMBER_A700 = 0xFF, 0xAB, 0x00
ORANGE = 0xFF, 0x98, 0x00
ORANGE_50 = 0xFF, 0xF3, 0xE0
ORANGE_100 = 0xFF, 0xE0, 0xB2
ORANGE_200 = 0xFF, 0xCC, 0x80
ORANGE_300 = 0xFF, 0xB7, 0x4D
ORANGE_400 = 0xFF, 0xA7, 0x26
ORANGE_500 = 0xFF, 0x98, 0x00
ORANGE_600 = 0xFB, 0x8C, 0x00
ORANGE_700 = 0xF5, 0x7C, 0x00
ORANGE_800 = 0xEF, 0x6C, 0x00
ORANGE_900 = 0xE6, 0x51, 0x00
ORANGE_A100 = 0xFF, 0xD1, 0x80
ORANGE_A200 = 0xFF, 0xAB, 0x40
ORANGE_A400 = 0xFF, 0x91, 0x00
ORANGE_A700 = 0xFF, 0x6D, 0x00
DEEP_ORANGE = 0xFF, 0x57, 0x22
DEEP_ORANGE_50 = 0xFB, 0xE9, 0xE7
DEEP_ORANGE_100 = 0xFF, 0xCC, 0xBC
DEEP_ORANGE_200 = 0xFF, 0xAB, 0x91
DEEP_ORANGE_300 = 0xFF, 0x8A, 0x65
DEEP_ORANGE_400 = 0xFF, 0x70, 0x43
DEEP_ORANGE_500 = 0xFF, 0x57, 0x22
DEEP_ORANGE_600 = 0xF4, 0x51, 0x1E
DEEP_ORANGE_700 = 0xE6, 0x4A, 0x19
DEEP_ORANGE_800 = 0xD8, 0x43, 0x15
DEEP_ORANGE_900 = 0xBF, 0x36, 0x0C
DEEP_ORANGE_A100 = 0xFF, 0x9E, 0x80
DEEP_ORANGE_A200 = 0xFF, 0x6E, 0x40
DEEP_ORANGE_A400 = 0xFF, 0x3D, 0x00
DEEP_ORANGE_A700 = 0xDD, 0x2C, 0x00
BROWN = 0x79, 0x55, 0x48
BROWN_50 = 0xEF, 0xEB, 0xE9
BROWN_100 = 0xD7, 0xCC, 0xC8
BROWN_200 = 0xBC, 0xAA, 0xA4
BROWN_300 = 0xA1, 0x88, 0x7F
BROWN_400 = 0x8D, 0x6E, 0x63
BROWN_500 = 0x79, 0x55, 0x48
BROWN_600 = 0x6D, 0x4C, 0x41
BROWN_700 = 0x5D, 0x40, 0x37
BROWN_800 = 0x4E, 0x34, 0x2E
BROWN_900 = 0x3E, 0x27, 0x23
GREY = 0x9E, 0x9E, 0x9E
GREY_50 = 0xFA, 0xFA, 0xFA
GREY_100 = 0xF5, 0xF5, 0xF5
GREY_200 = 0xEE, 0xEE, 0xEE
GREY_300 = 0xE0, 0xE0, 0xE0
GREY_400 = 0xBD, 0xBD, 0xBD
GREY_500 = 0x9E, 0x9E, 0x9E
GREY_600 = 0x75, 0x75, 0x75
GREY_700 = 0x61, 0x61, 0x61
GREY_800 = 0x42, 0x42, 0x42
GREY_900 = 0x21, 0x21, 0x21
BLUE_GREY = 0x60, 0x7D, 0x8B
BLUE_GREY_50 = 0xEC, 0xEF, 0xF1
BLUE_GREY_100 = 0xCF, 0xD8, 0xDC
BLUE_GREY_200 = 0xB0, 0xBE, 0xC5
BLUE_GREY_300 = 0x90, 0xA4, 0xAE
BLUE_GREY_400 = 0x78, 0x90, 0x9C
BLUE_GREY_500 = 0x60, 0x7D, 0x8B
BLUE_GREY_600 = 0x54, 0x6E, 0x7A
BLUE_GREY_700 = 0x45, 0x5A, 0x64
BLUE_GREY_800 = 0x37, 0x47, 0x4F
BLUE_GREY_900 = 0x26, 0x32, 0x38
WHITE = 0xFF, 0xFF, 0xFF
BLACK = 0x00, 0x00, 0x00
