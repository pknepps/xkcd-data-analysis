---
marp: true
---

<!--
theme: gaia
class: lead
-->

<style>
section {
    font-size: 250%;
}
</style>

# XKCD Comic Analysis

## Preston Knepper and Kevin McCall

### May 7, 2024

![bg right:38% 120%](https://www.adenin.com/assets/logos/xkcd.png)

---

# Background

XKCD refers to itself as "A web-comic of romance, sarcasm, math, and language", taking its roots in nerdy humor typically about technology, math, physics and science. XKCD is popular in the world covered by those topics. The comic i posted regularly on every Monday, Wednesday, and Saturday.

![bg right:40% 95%](https://imgs.xkcd.com/comics/machine_learning.png)

---

## Gathering the Data

Monroe offers an API for his comic, which only requires the parsing of jsons into a .csv which R can read. In spite of this, the data was pretty tricky to form into a .csv. The reason why quickly became the bane of this project.

The json has several fields, which will be the attributes of the .csv.

![bg left 95%](https://imgs.xkcd.com/comics/data_trap.png)

---

<!-- header: Gathering the Data-->
<style scoped>
section {
    font-size: 200%
}
</style>

#### A look at the JSON

![bg right:20%](./json.png)

-   month: The month of the the year this comic was posted (as a number).
-   num: The comic number.
    link: An external link on image click.
    -year: The year the comic was posted.
-   news: Comic news to display to the reader.
-   safe_titl: A version of the title safe for all browsers.
-   transcript: The bane of this project.
-   alt: The alt text (mouseover) of the comic.
-   img: A link to the comic image.
-   t

---

# Parsing the Data

## Stage by stage process

Unlike parsing the scenery, parsing dialog is **hard**.

---

### Analyzing the problem

Here is an example comic to parse text from:

![](https://imgs.xkcd.com/comics/vacuum_2x.png)

---

[[Beret Guy is heaving a vacuum cleaner overhead]]\n\nCueball: What are you doing?\n[[Beret guy sets the vacuum cleaner on the ground as one would normally use it, but is standing atop the engine and desperately manhandling the grip.]]\nBeret: Trying to unlock the tremendous energy of the vacuum.\n\n[[Beret guy rises off the ground, hovering on the vacuum cleaner]\nCueball: That's not what that-\nBeret: Ha ha! It works!\n<<BWAROUUGUMHGHHGMMM>>\n\nCueball: I said, that's-\nBeret: The univere is mine to command!\n<<GLHDFKUOUAHUUUUGUUUAAAUUAUUUUUUUGGGGGH>>\n[[Beret guy rockets away on plume of Clean Energy]]\n\n{{Title text: Do you think you could actually clean the living room at some point, though?}}"

---

xkcd comics transcripts are in theatrical format. Each dialog is on its own line and is preceeded by who is saying it. Our strategy to parse this data will be to search for text on a new like and split the character and their speech by a colon.

The easiest way to parse data in this format is to break it down into simpler stages and tackle those one at a time.

---

### First Stage - Cleaning text

First, lets remove the data we do not need

The {{Title Text}} is unecessary since our web scraping script has access to that field already, so we may remove it.

---

[[Beret Guy is heaving a vacuum cleaner overhead]]\n\nCueball: What are you doing?\n[[Beret guy sets the vacuum cleaner on the ground as one would normally use it, but is standing atop the engine and desperately manhandling the grip.]]\nBeret: Trying to unlock the tremendous energy of the vacuum.\n\n[[Beret guy rises off the ground, hovering on the vacuum cleaner]\nCueball: That's not what that-\nBeret: Ha ha! It works!\n<<BWAROUUGUMHGHHGMMM>>\n\nCueball: I said, that's-\nBeret: The univere is mine to command!\n<<GLHDFKUOUAHUUUUGUUUAAAUUAUUUUUUUGGGGGH>>\n[[Beret guy rockets away on plume of Clean Energy]]\n\n

---

### Second Stage - Extracting Scene information

-   \\[\\[

    -   \\[ matches a left square bracket, so this pattern matches [[

-   \\([^\\]]\*)

    -   The capturing group is created with the ()
    -   Inside the capturing group, we have [^\\]]_
        -The _ matches the the previous item, [^\\]] 0 or more times - This is a negative scanset, matching character that are not contained in it - This will not match the ] character,
    -   This uses a capturing group to match characters that are not a ]

-   \\]\\]

---

\n\nCueball: What are you doing?\n\nBeret: Trying to unlock the tremendous energy of the vacuum.\n\n\nCueball: That's not what that-\nBeret: Ha ha! It works!\n<<BWAROUUGUMHGHHGMMM>>\n\nCueball: I said, that's-\nBeret: The univere is mine to command!\n<<GLHDFKUOUAHUUUUGUUUAAAUUAUUUUUUUGGGGGH>>\n\n\n

---

### Clean up from Stage 2

Many \n's remain. Furthermore, characters' dialog can span multiple lines.
We may flatten these into a single pair \n by making a call to `str_replace`, replacing `\n+` with a single `\n`.

However, since newlines can be anywhere in a character's dialog, we can't use a simple regex to parse text.

---

### Solution: A complicated Regex

# `(?:\\n)(?!(?:.(?!\\n))+:)`

-   This regex uses _lookaheads_, a powerful regex feature that determines matches without capturing the input.

-   Lookaheads are used to match a select a \n where there is another \n in between it and the next : character

-   These are removed with a call to `str_remove_all`

---

[[Beret Guy is heaving a vacuum cleaner overhead]]\n\nCueball: What are you doing?\n[[Beret guy sets the vacuum cleaner on the ground as one would normally use it, but is standing atop the engine and desperately manhandling the grip.]]\nBeret: Trying to unlock the tremendous energy of the vacuum.\n\n[[Beret guy rises off the ground, hovering on the vacuum cleaner]\nCueball: That's not what that-\nBeret: Ha ha! It works!\n<<BWAROUUGUMHGHHGMMM>>\n\nCueball: I said, that's-\nBeret: The univere is mine to command!\n<<GLHDFKUOUAHUUUUGUUUAAAUUAUUUUUUUGGGGGH>>\n[[Beret guy rockets away on plume of Clean Energy]]\n\n

---

# Results

---

## Successes

---

## Issues

---

### Non-obvious delimiters

Since the way we parse data is dependent on the ":" symbol, we are at the mercy of Monroe to provide to be consistent in his theatrical format. However, there are exceptions. For example:

---

![obaoo](https://www.explainxkcd.com/wiki/images/2/26/encryptic.png)

---
