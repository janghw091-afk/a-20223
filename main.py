# 기존 (오류 발생 부분)
# daily_total['기준일자'].dt.replace(day=1).dt.weekday

# 수정 후 (dt.floor('MS') 사용)
daily_total["월_주차"] = (
    daily_total["기준일자"].dt.strftime("%Y-%m")
    + " "
    + (
        (
            daily_total["기준일자"].dt.day
            + daily_total["기준일자"].dt.floor("MS").dt.weekday
        )
        // 7
        + 1
    ).astype(str)
    + "주차"
)
