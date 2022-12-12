import datetime
import pytz


def nowfun(timezone):
    return datetime.datetime.now(pytz.timezone(timezone))


def nowfun_us():
    return nowfun("America/New_York")


def nowfun_ns():
    return nowfun("Asia/Calcutta")


def nowfun_hk():
    return nowfun("Asia/Hong_Kong")


def nowfun_cet():
    return nowfun("CET")


def nowfun_l():
    return nowfun("Europe/London")


def nowfun_asx():
    return nowfun("Australia/Brisbane")


def nowfun_t():
    return nowfun("Asia/Tokyo")


def nowfun_ss():
    return nowfun("Asia/Shanghai")


def nowfun_ks():
    return nowfun("Asia/Seoul")


def nowfun_jk():
    return nowfun("Asia/Jakarta")


def nowfun_sa():
    return nowfun("America/Sao_Paulo")


def nowfun_sr():
    return nowfun("Asia/Riyadh")


def nowfun_he():
    return nowfun("Europe/Helsinki")


def nowfun_tw():
    return nowfun("Asia/Taipei")


def nowfun_ls():
    return nowfun("Europe/Lisbon")


def nowfun_ir():
    return nowfun("Europe/Dublin")


def nowfun_jo():
    return nowfun("Africa/Johannesburg")


CLOSING_HOURS = [
    {
        "countries": [
            "US",
            "TO",
            "V",
            "CN",
        ],  # US, Canada [Toronto], Canada [TSXV], Canada [Canadian Sec]
        "hour": 16,
        "minute": 0,
        "nowfun": nowfun_us,
    },
    {
        "countries": ["NS"],  # India
        "hour": 15,
        "minute": 30,
        "nowfun": nowfun_ns,
    },
    {
        "countries": ["HK"],  # Hong Kong
        "hour": 16,
        "minute": 0,
        "nowfun": nowfun_hk,
    },
    {
        "countries": [
            "DE",
            "F",
            "ST",
            "PA",
            "AS",
            "BR",
            "MI",
            "MC",
        ],  # Germany [XETRA], Germany [Frankfurt], Sweden [Stockholm], France [Paris], Netherlands [Amsterdam], Belgium [Brussels], Italy [Milan], Spain [Madrid]
        "hour": 17,
        "minute": 30,
        "nowfun": nowfun_cet,
    },
    {
        "countries": ["L"],  # UK [London]
        "hour": 16,
        "minute": 30,
        "nowfun": nowfun_l,
    },
    {
        "countries": ["SW"],
        "hour": 17,
        "minute": 20,
        "nowfun": nowfun_cet,
    },  # Switzerland
    {
        "countries": ["OL"],  # Norway [Oslo]
        "hour": 16,
        "minute": 20,
        "nowfun": nowfun_cet,
    },
    # {
    #     "countries": ["ME"], # Russia [Moscow]
    #     "hour": 18,
    #     "minute": 39,
    #     "timezone": "Europe/Moscow"
    # },
    {
        "countries": ["ASX"],  # Australia
        "hour": 16,
        "minute": 0,
        "nowfun": nowfun_asx,
    },
    {
        "countries": ["T"],  # Japan [Tokyo]
        "hour": 15,
        "minute": 0,
        "nowfun": nowfun_t,
    },
    {
        "countries": ["SS", "SZ"],  # China [Shanghai], China ["Shenzen"]
        "hour": 15,
        "minute": 0,
        "nowfun": nowfun_ss,
    },
    {
        "countries": ["KS"],  # South Korea
        "hour": 15,
        "minute": 30,
        "nowfun": nowfun_ks,
    },
    {
        "countries": ["JK"],  # Indonesia [Jakarta]
        "hour": 15,
        "minute": 0,
        "nowfun": nowfun_jk,
    },
    {
        "countries": ["SA"],  # Brazil [Sao Paulo]
        "hour": 17,
        "minute": 0,
        "nowfun": nowfun_sa,
    },
    {
        "countries": ["SR"],  # Saudi Arabia
        "hour": 15,
        "minute": 0,
        "nowfun": nowfun_sr,
    },
    {
        "countries": ["HE"],  # Finland [Helsinki]
        "hour": 18,
        "minute": 25,
        "nowfun": nowfun_he,
    },
    {
        "countries": ["WA"],  # Poland [Warsaw]
        "hour": 16,
        "minute": 50,
        "nowfun": nowfun_cet,
    },
    {
        "countries": ["TW", "TWO"],  # Taiwan, Taiwan [Taipei]
        "hour": 13,
        "minute": 30,
        "nowfun": nowfun_tw,
    },
    {
        "countries": ["CO"],
        "hour": 16,
        "minute": 55,
        "nowfun": nowfun_cet,
    },  # Denmark [CO]
    {
        "countries": ["LS"],  # Portugal [LS]
        "hour": 16,
        "minute": 30,
        "nowfun": nowfun_ls,
    },
    {
        "countries": ["IR"],  # Ireland
        "hour": 17,
        "minute": 28,
        "nowfun": nowfun_ir,
    },
    {
        "countries": ["JO"],  # South Africa
        "hour": 17,
        "minute": 0,
        "nowfun": nowfun_jo,
    },
]
