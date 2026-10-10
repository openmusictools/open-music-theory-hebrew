# תאוריית המוזיקה הפתוחה — המהדורה העברית

אתר קריאה חדש בעברית, המבוסס על תרגום Open Music Theory גרסה 1.

- [אתר הספר](https://openmusictools.github.io/open-music-theory-hebrew/)
- [מהדורות והורדות](https://github.com/openmusictools/open-music-theory-hebrew/releases)
- [מאגר התרגום](https://github.com/open-music-theory-he/open-music-theory-hebrew)

התרגום בסיוע AI, עם תיעוד בדיקות והערות. מהדורת הבטא טרם עברה הגהה מקצועית אנושית מלאה. תמונות ומסמכים מקוריים עשויים להישאר באנגלית. ספר השמע חלקי.

## פרסום

קובץ `publish.py` בונה אתר סטטי של כל עמודי הספר ותיעוד התרגום, עם חיפוש, ניווט, שינוי גודל כתב ומצב כהה. הוא מאמת קישורים מקומיים ועוגנים. המאגר הציבורי המקורי נשאר מקור התוכן; עותק שלו נשלף לכל בנייה.

GitHub Pages משתמש ב־GitHub Actions כמקור פרסום. האתר מתעדכן עם שינויים בקוד, פרסום ריליס ובכל יום. ההורדות נטענות מהריליס האחרון שמכיל את שש החבילות, לרבות ריליס בטא. קובץ `release.json` באתר משמש גיבוי כאשר GitHub API אינו זמין בדפדפן.

להפקת ריליס חדש, הפעילו את `Publish Hebrew book website and releases` ב־Actions עם תג חדש, למשל `v0.1.0-beta.2`. השאירו תג ריק לעדכון האתר בלבד. אפשר לקבע את `source_ref` ל־commit לצורך שחזור. תג קיים אינו מוחלף.

כל ריליס מכיל PDF; PDF עם נספחים; שמע; שמע עם נספחים; כל הפלטים ללא קבצי מקור; וכל החומר כולל קבצי מקור ומצב השמע השמור. חבילות הפלטים אינן מכילות Markdown, קוד, קבצי תיווי לעריכה, גיבויים או מקטעי שמע חלקיים. חבילת המקור שומרת גם אותם. ה־PDF הוא היצוא הסטטי המלא, הכולל מסמכים בעקבות הפרקים ותיעוד המהדורה.

תהליך הפרסום משתמש רק בשמע שכבר נשמר בענף `audiobook-data` של מאגר התרגום; אין שימוש ב־Gemini API ואין יצירת קריינות מחדש. המשך יצירת השמע נשאר בתהליך הקיים במאגר התרגום. מספר הפרקים המוקלטים, מזהי מקור, גדלים וחתימות SHA256 נשמרים בכל ריליס ב־`release-manifest.json`.

## קרדיטים ורישיונות

מקור הספר: Kris Shaffer, Bryn Hughes ו־Brian Moseley; עריכה: Kris Shaffer ו־Robin Wharton; פרסום: Hybrid Pedagogy Publishing. זו מהדורה עברית עצמאית, שאינה מוצגת כתרגום רשמי המאושר בידי המחברים.

טקסט הספר והעיבוד העברי: **CC BY-SA 4.0**. רישיונות פרטניים של מדיה וקוד מקור נשמרים במאגר המקור. איורי האתר המופשטים החדשים נוצרו עבור המהדורה ומוקדשים לנחלת הכלל תחת **CC0 1.0**; אין בהם כלי נגינה. קוד האתר החדש: **MIT**.

MIT License — Copyright (c) 2026 Hebrew edition contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the Software), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software. THE SOFTWARE IS PROVIDED AS IS, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
