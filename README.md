# Competitve Programming Parser for Sublime Text 3

This is a Sublime Text package for parsing problem test-cases from various online judges. You can then run your solution against the testcases with the help of [CppFastOlympicCoding](https://packagecontrol.io/packages/CppFastOlympicCoding). The list of supported websites can be found [here](https://github.com/jmerle/competitive-companion#supported-websites).

Competitive Programming Parser can:

-   parse testcases for a problem
-   parse a problem : creates file and parses testcases for the problem
-   parse a contest : parses all the problems of a contest

<u><b>Dependencies</b></u>

-   [Competitive Companion](https://github.com/jmerle/competitive-companion)
-   [FastOlympicCoding](https://github.com/Jatana/FastOlympicCoding)

<u><b>Setup</b></u>

-   Make sure you have `python3`, [FastOlympicCoding](https://github.com/Jatana/FastOlympicCoding) and [Competitive Companion](https://github.com/jmerle/competitive-companion) installed.
-   Add `12345` in the list of ports of competitive-companion browser extension.
-   Clone the [repository](https://github.com/DrSchwad/FastOlympicCodingHook) inside your Sublime Text Packagse

<u><b>Usage</b></u>

1.
    -   For parsing the test-cases for a particular file: Right click anywhere in the file and select `CompetitveProgammingParser -> Parse Testcases`.
    Key Binding: <kbd>ctrl+shift+x</kbd>
    -  For parsing a problem: Right click anywhere in the Sublime Text editor and select `CompetitveProgammingParser -> Parse Problem`.
    Key Binding: <kbd>ctrl+shift+y</kbd>
    -  For parsing a contest: Right click anywhere in the Sublime Text editor and select `CompetitveProgammingParser -> Parse Contest`.
    Key Binding: <kbd>ctrl+shift+c</kbd>
2. In the browser, navigate to the problem page and click on the competitive-companion extension's `green plus icon`.
3. Use [CppFastOlympicCoding](https://packagecontrol.io/packages/CppFastOlympicCoding) to run the solution against the parsed testcases.