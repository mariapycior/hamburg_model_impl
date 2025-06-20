import re

# Odczytaj zawartość pliku
with open('plot_utils.py', 'r') as f:
    content = f.read()

# Zastąp nawiasy okrągłe na kwadratowe
content = re.sub(r'Integrated Luminosity \(fb\${\^-1\}\)', 'Integrated Luminosity [fb${^-1}]', content)

# Zapisz zmiany
with open('plot_utils.py', 'w') as f:
    f.write(content)
