from vietnam_number.number2word import n2w, n2w_single
import re

from .datestime_vi import _remove_prefix_zero

from .symbol_vi import vietnamese_set, vietnamese_without_num_re


_negative_symbol_re = r"(.)(-{1})?"
_normal_number_re = r"[\d]+"
_number_with_one_middle_space_re = r"[\d]+[\s]{1}[\d]{3}"
_number_with_two_middle_space_re = r"[\d]+[\s]{1}[\d]{3}[\s]{1}[\d]{3}"
_number_with_three_middle_space_re = r"[\d]+[\s]{1}[\d]{3}[\s]{1}[\d]{3}[\s]{1}[\d]{3}"
_number_with_one_dot_middle_re = r"[\d]+[.]{1}[\d]{3}"
_number_with_two_dot_middle_re = r"[\d]+[.]{1}[\d]{3}[.]{1}[\d]{3}"
_number_with_three_dot_middle_re = r"[\d]+[.]{1}[\d]{3}[.]{1}[\d]{3}[.]{1}[\d]{3}"
_float_number_re = r"[\d]+[,]{1}[\d]+"

_phone_re = r"(((\+84|84|0|0084){1})(3|5|7|8|9))+([0-9]{8})"

_prefix_range = r"(từ|tới|còn|đến|khoảng|sau)"

_end_number_re = (
    r"(-)?("
    + _float_number_re
    + "|"
    + _number_with_three_dot_middle_re
    + "|"
    + _number_with_two_dot_middle_re
    + "|"
    + _number_with_one_dot_middle_re
    + "|"
    + _number_with_three_middle_space_re
    + "|"
    + _number_with_two_middle_space_re
    + "|"
    + _number_with_one_middle_space_re
    + "|"
    + _normal_number_re
    + r")"
)
_number_re = (
    _negative_symbol_re
    + r"("
    + _float_number_re
    + "|"
    + _number_with_three_dot_middle_re
    + "|"
    + _number_with_two_dot_middle_re
    + "|"
    + _number_with_one_dot_middle_re
    + "|"
    + _number_with_three_middle_space_re
    + "|"
    + _number_with_two_middle_space_re
    + "|"
    + _number_with_one_middle_space_re
    + "|"
    + _normal_number_re
    + r")"
)

_multiply_number_re = "(" + _normal_number_re + r")(x|\sx\s)(" + _normal_number_re + ")"

_range_number_re = re.compile(
    _prefix_range
    + _number_re
    + r"(-|\s\-\s)"
    + _end_number_re
    + vietnamese_without_num_re,
    re.IGNORECASE,
)
_special_ordinal_pattern = r"(thứ|hạng)(\s)(1|4)"


def _expand_number(match):
    prefix, negative_symbol, number = match.groups(0)
    number = _remove_prefix_zero(number)

    if "," in number and not re.fullmatch(r"\d+(,\d{3})+", number):
        parts = number.split(",")
        integer_part = n2w(parts[0])
        decimal_part = " ".join([n2w_single(d) for d in parts[1]])
        word = integer_part + " phẩy " + decimal_part
    else:
        word = n2w(number)

    if prefix in vietnamese_set:
        negative_symbol = "" if negative_symbol == 0 else negative_symbol
        return prefix + " " + negative_symbol + word + " "
    else:
        word = "-" + word if negative_symbol == "-" else word
        return prefix + " " + word + " "


def _expand_phone(match):
    text: str = match.group(0).strip().rstrip()
    return n2w_single(text)


def _expand_range(match):
    (
        prefix0,
        prefix1,
        negative_symbol1,
        number_start,
        space,
        negative_symbol2,
        number_end,
        ending,
    ) = match.groups(0)
    print(
        f"prefix0: {prefix0}, prefix1: {prefix1}, negative_symbol1: {negative_symbol1}, number_start: {number_start}, space: {space}, negative_symbol2: {negative_symbol2}, number_end: {number_end}, ending: {ending}"
    )
    prefix1 = "" if prefix1 == 0 else prefix1
    if prefix1 in vietnamese_set:
        return match.group(0)
    else:
        number_start = "-" + number_start if negative_symbol1 == "-" else number_start
        number_end = "-" + number_end if negative_symbol2 == "-" else number_end
        return (
            prefix0 + prefix1 + n2w(number_start) + " đến " + n2w(number_end) + ending
        )


def _expand_ordinal(match):
    prefix, space, number = match.groups(0)
    if number == "1":
        return prefix + space + "nhất"
    elif number == "4":
        return prefix + space + "tư"
    else:
        return prefix + space + n2w(number)


def _expand_multiply_number(match):
    number1, multiphy_symbol, number2 = match.groups(0)
    return n2w(number1) + " nhân " + n2w(number2)


_comma_number_re = re.compile(r"([0-9][0-9\,]+[0-9])")


def _remove_commas(m):
    return m.group(1).replace(",", "")


_special_number_spell_out_re = re.compile(
    r"(?i)(số cuối|otp|ô tê pê|cmnd|cccd|căn cước|số điện thoại|sđt|liên hệ|l/h)(\D+)(\d{4,})"
)


def _expand_special_number(match):
    prefix = match.group(1)
    middle = match.group(2)
    number = match.group(3)
    spelled_out = n2w_single(number)
    return prefix + middle + spelled_out


def normalize_number_vi(text):
    text = re.sub(_special_number_spell_out_re, _expand_special_number, text)
    text = re.sub(_comma_number_re, _remove_commas, text)
    text = re.sub(_special_ordinal_pattern, _expand_ordinal, text)
    text = re.sub(_multiply_number_re, _expand_multiply_number, text)
    text = re.sub(_range_number_re, _expand_range, text)
    text = re.sub(_phone_re, _expand_phone, text)
    text = re.sub(_number_re, _expand_number, text)
    return text
