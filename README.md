<p>
  <img src="https://raw.githubusercontent.com/crnobog69/py-ffmpeg/main/%D0%A0%D0%B5%D1%81%D1%83%D1%80%D1%81%D0%B8/PyFFmpeg.png" width="70%">
</p>

<br>
Ово је **једноставан** графички интерфејс за FFmpeg написан у Python-у са PyQt5.
This is **a simple gui** for FFmpeg written in Pyhton with PyQt5.
---

> [!CAUTION]
> <br>
 ```bash
Traceback (most recent call last):
  File "/home/krematorijum/Desktop/py-ffmpeg.py", line 254, in updateProgress
    self.duration = int(duration_parts[0]) * 3600 + int(duration_parts[1]) * 60 + float(duration_parts[2])
                    ^^^^^^^^^^^^^^^^^^^^^^
ValueError: invalid literal for int() with base 10: 'N/A'
[1]    3453 IOT instruction (core dumped)  python py-ffmpeg.py
```


<br>
<br>
<br>


> [!CAUTION]
> Језик \\|/ Language

| Фајл               | Језик (Српски)          | Language (English)    |
|--------------------|--------------------------|-----------------------|
| prevod_sr_RS.qm    | На српском језику        | In Serbian language   |
| prevod_en_US.qm    | На енглеском језику      | In English language   |
| prevod_ru_RU.qm  | На руском језику         | In Russian language   |
| prevod_ja_JP.qm    | На јапанском језику      | In Japanese language  |


---


<br>

> [!IMPORTANT]
> 1.
> <br>
> Иконица тренутно не ради на Arch Linux (EndeavourOS/KDE Plasma 6.1/ Wayland)
> <br>
> Icon doesn't work at the time on Arch Linux (EndeavourOS/KDE Plasma 6.1/ Wayland)

---

**Тема је инспирисана палетом боја из [Catppuccin](https://github.com/catppuccin).**
<br>
**Theme inspired by the color palette from [Catppuccin](https://github.com/catppuccin).**


---

#### README на српском 🇷🇸

# Графички интерфејс за [FFmpeg](https://github.com/FFmpeg/FFmpeg) 🎬

> [Read in English 🇬🇧](#readme-in-english)

Добродошли у репозиторијум за GUI апликацију за FFmpeg! Ова апликација вам омогућава да лако конвертујете мултимедијалне фајлове у различите формате користећи FFmpeg.

## 📋 Садржај

- [Упутство за покретање](#упутство-за-покретање-)
- [Карактеристике](#карактеристике-)
- [Завршетак конверзије](#завршетак-конверзије-)
- [Допринос](#допринос-)
- [Лиценца](#лиценца-)

<br>

## Упутство за покретање 🚀

1. Уверите се да имате инсталиран FFmpeg. Можете га преузети са [FFmpeg званичне странице](https://ffmpeg.org/download.html).
2. Клонирајте овај репозиторијум:
   ```bash
   git clone https://github.com/crnobog69/py-ffmpeg.git
   ```
3. Инсталирајте потребне Python библиотеке:
   ```bash
   pip install pyqt5
   ```
4. Покрените апликацију:
   ```bash
   python py-ffmpeg.py
   ```

<br>

## Карактеристике 🌟

- Избор улазних и излазних datoteka 🎥🎵
- Избор формата (видео, аудио, слике) 📂
- Прогрес бар за праћење напредовања преображавања ⏳
- Упозорења за неслагање формата ⚠️
- Прилагођени изглед са темом 🌌

<br>

## Допринос 🤝

Доприноси су добродошли! Ако желите да допринесете, молимо вас да:

1. Форкујте репозиторијум
2. Направите нову грану (`git checkout -b feature/AmazingFeature`)
3. Commit-ујте ваше промене (`git commit -m 'Add some AmazingFeature'`)
4. Push-ујте на грану (`git push origin feature/AmazingFeature`)
5. Отворите Pull Request

<br>

## Лиценца 📄

Дистрибуирано под MIT лиценцом. Погледајте `LICENSE` за више информација.

---

⭐️ Ако вам се свиђа овај пројекат, молимо вас да му дате звездицу!

---

#### README in English 🇬🇧

# GUI Application for [FFmepg](https://github.com/FFmpeg/FFmpeg)🎬

> [Читај на српском 🇷🇸](#readme-на-српском)

Welcome to the repository for the FFmpeg GUI application! This app allows you to easily convert multimedia files into various formats using FFmpeg.

## 📋 Contents

- [Getting Started](#getting-started-)
- [Features](#features-)
- [Conversion Completion](#conversion-completion-)
- [Contributing](#contributing-)
- [License](#license-)

<br>

## Getting Started 🚀

1. Make sure you have FFmpeg installed. You can download it from the [FFmpeg official site](https://ffmpeg.org/download.html).
2. Clone this repository:
   ```bash
   git clone https://github.com/crnobog69/py-ffmpeg.git
   ```
3. Install the required Python libraries:
   ```bash
   pip install pyqt5
   ```
4. Run the application:
   ```bash
   python py-ffmpeg.py
   ```

<br>

## Features 🌟

- Input and output file selection 🎥🎵
- Format selection (video, audio, image) 📂
- Progress bar to track conversion progress ⏳
- Format mismatch warnings ⚠️
- Custom appearance with a theme 🌌

<br>

## Contributing 🤝

Contributions are welcome! If you'd like to contribute, please:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<br>

## License 📄

Distributed under the MIT License. See `LICENSE` for more information.

---

⭐️ If you like this project, please give it a star!

---
