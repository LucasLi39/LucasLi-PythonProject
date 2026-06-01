# JLPT N5 + N4 kanji — considered "common" and will NOT get furigana annotations

N5_KANJI = set(
    "一二三四五六七八九十百千万円時分後前午上下左右中大小月火水木金土日"
    "人口目耳手足力正生青白赤黒"
    "学学校先生私本語文数学音楽体育"
    "何誰どこ高低新古多少強弱長短明暗"
    "春夏秋冬朝昼夕夜雨雪風雲空山川海池林花鳥魚犬猫牛馬"
    "車電気間時間有名"
    "父母亲兄弟姉妹友"
    "右左前後中"
    "年生先"
)

N4_KANJI = set(
    "会議員社国東西南北"
    "業者発方新場"
    "話語読書"
    "行来帰"
    "食物飲買"
    "仕事休"
    "住居館"
    "電話"
    "病院"
    "駅道"
    "店銀"
    "門戸"
    "部屋"
    "窓"
    "天窓"
    "階"
    "建物"
    "橋"
    "港"
    "空港"
    "公園"
    "動物"
    "植物"
    "科"
    "音"
    "声"
    "歌"
    "画"
    "映画"
    "写真"
    "新聞"
    "雑誌"
    "辞書"
    "紙"
    "鉛筆"
    "筆"
    "鍵"
    "傘"
    "財布"
    "鞄"
    "服"
    "靴"
    "帽子"
    "眼鏡"
    "時計"
)

# Combine all common kanji
COMMON_KANJI = N5_KANJI | N4_KANJI


def is_uncommon(kanji_char: str) -> bool:
    """Return True if the kanji is uncommon (should get furigana)."""
    return kanji_char not in COMMON_KANJI
