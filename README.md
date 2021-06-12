# LeMonde on e-book with Selenium

A recipe using Selenium and ebooklib to get LeMonde Abonné as a epub ebook.
It then calls calibre for conversion to mobi and uses the email library to send the file to the kindle.

For people with Windows, I compiled the program with pyinstaller already.

Make sure you have the right chromedriver.exe or geckdriver.exe in the "/Driver" folder depending on your browser and browser version.

You can fill the parameter files (otherwise you will be prompted to do it during the program launch), but DO NOT FILL the password field (you will be prompted to enter you email and lemonde password and it will be kind of encoded in the txt file).

Advice: Check the code, change the encoding key to your own personal key and compile the program yourself for added safety. Then crate an automatic task with a task scheduler to have the program run automatically every day.

You might wonder why there is so much random "sleeping" time in the code, first if you don't wait long enough you scrap the page before it is fully loaded, second it was also an attempt to make to bot less recognisable by its behaviour.
