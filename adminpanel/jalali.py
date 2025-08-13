# utils/jalali.py
from django import forms

def fa_to_en_digits(s: str) -> str:
    if not isinstance(s, str):
        return s
    return s.translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789'))

class JalaliOrGregorianDateField(forms.DateField):
    """
    Accepts:
      - 'YYYY/MM/DD' or 'YYYY-MM-DD' with Persian or Latin digits.
      - If year < 1700 → treat as Jalali and convert via jdatetime.
      - Else → treat as Gregorian and defer to DateField parsing.
    Returns a Python datetime.date.
    """
    def to_python(self, value):
        if not value:
            return None

        s = fa_to_en_digits(str(value).strip())
        # unifies separators
        s2 = s.replace('-', '/')
        parts = s2.split('/')

        # Detect Jalali by year range (safe heuristic)
        if len(parts) == 3 and all(p.isdigit() for p in parts):
            y, m, d = map(int, parts)
            if y < 1700:  # Jalali
                import jdatetime
                try:
                    gdate = jdatetime.date(y, m, d).togregorian()  # datetime.date
                    return gdate
                except Exception:
                    # fall through to default parsing to raise a clean ValidationError
                    pass

        # Gregorian fallback: allow both '-' and '/'
        # Let DateField handle it (with input_formats you set when constructing the field)
        return super().to_python(s)
