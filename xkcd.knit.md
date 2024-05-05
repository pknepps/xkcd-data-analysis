---
title: "XKCD: a Semi-Serious Analysis of a Non-Serious Comic"
author: "Preston Knepper and Kevin McCall"
date: "2024-04-18"
output: html_document
---



# Introdution

In this study, we will analyze commonalities and frequencies of various items in the xkcd. XKCD is a web comic written by Randall Munroe, a CNU graduate with a degree in physics. Before writing comics full time, he previously had worked on robotics at NASA.

XKCD refers to itself as "A web-comic of romance, sarcasm, math, and language", taking its roots in nerdy humor typically about technology, math, physics and science. XKCD is popular in the world covered by those topics. The chances of you being in this class (Math 474) and never seeing an xkcd comic are slim to none. The comic was originally started on LiveJournal on September 30, 2005, with an upload of 13 images. It quickly gain popularity and it was moved to his own server, xkcd.com, on January 1, 2006. Since then, the comic has been posted regularly on every Monday, Wednesday, and Saturday. 

The web-comic features many topics and loved characters (despite the comic made up of almost entirely stick figures). These topics are mostly STEM related, but can also be about politics, language, and sometimes just feature bizarre and random humor -- like most comics featuring Beret Guy. Some popular characters from the comic include [Cueball](https://www.explainxkcd.com/wiki/index.php/Cueball), [Black Hat](https://www.explainxkcd.com/wiki/index.php/Black_Hat), the previously mentioned [Beret Guy](https://www.explainxkcd.com/wiki/index.php/Beret_Guy), and Cueball's girlfriend, [Megan](https://www.explainxkcd.com/wiki/index.php/Megan). For the most part, the characters have little story and are mostly used to expand on the humor in an individual comic.

In this paper, we will observe the transcripts of these comics, as well as unique properties about some of the comics and the dates they were posted.

# The data
We will be using the tidyverse package throughout this project. We will go ahead and include it now.

```r
if (!require("tidyverse")) {
  install.packages("tidyverse")
}
library("tidyverse")
```

The .csv below contains data on every single xkcd comic. Most importantly, the transcript of every comic. It's a good idea to run the python file, extractDataset.py, before viewing this file for the first time, as a comic is posted three times every week. Monroe offers an API for his comic, which only requires the parsing of jsons into a .csv which R can read.

```r
xkcd <- read.csv("xkcd.csv", quote = "")
nrow(xkcd)
```

```
## [1] 2927
```
From the summary, we get information on the metadata of the comic. A comic has the following attributes:

* num: The comic number, this is simply a unique key assigned chronologically.
* year, month, day: the date the comic was posted. All as integers.
* title: The title of the comic.
* safe_title: The title of the comic. A section of this paper will be dedicated to finding differences between the two.
* transcript: A transcript of this comic. Includes dialog and image descriptions.
* alt: The alt-text found by mousing over the comic.
* img: A url to the image of the comic.
* link: An link to an external site found by clicking the comic. Few comics utilize this.
* news: News updates. Rare, but typically about upcoming publications.
* extra_parts: Occasionally, Monroe will post a game, or other type of interactive comic. Information about it will be posted as a json here. For simplicities sake, this attribute contains the first value of said nested json.

# Cleaning the data

The first thing to do is to convert the three separate attributes year, month, day into a single value date_posted. It will also be useful to add a day_of_week attribute, which includes the day of the week the comic was posted. The day of the week will probably be more useful than just the date as the comic is posted regularly on mondays, wednesdays, and fridays.


```r
xkcd_date <- xkcd |> unite(date, month, day, year, sep = "-") |> mutate(date = as.Date(mdy(date))) |> mutate(weekday = wday(date, label = TRUE),.after = date)
```
Another thing to note is that the transcript includes a physical description of the comic itself. Sorry blind readers, but we do not care for this. We will remove these parts using regex's. Note Image descriptors are wrapped in "[[]]". Note that the alt text is also included here (wrapped in "\{\{\}\}"), since there is already a section for alt text, we will remove it. The final part to remove are the screenplay names (e.g. "Man:", "Woman:") as they only indicate who is speaking, and are not part of the actual text of the comic.


Okay, time to tidy transcript.

There are 2 challenges in doing this 
- scenebuilding is described in [[]]
- Dialogue is in the format Person: says something (we thought)


## Parsing the [[scenebuilding]]
![I_Know_Regular_Expressions](https://imgs.xkcd.com/comics/regular_expressions.png)

This was fairly simple, we used stringr and str_match_all to separate the text inside the double square brackets
our regex ended up like this: \\[\\[([^\\]]*)\\]\\]
- \\[\\[
    - \\[ matches a left square bracket, so this pattern matches [[

- \\([^\\]]*)
    - The capturing group is created with the ()
    - Inside the capturing group, we have [^\\]]*
        -The * matches the the previous item, [^\\]] 0 or more times
            - This is a negative scanset, matching character that are not contained in it
            - This will not match the ] character, 
    - This uses a capturing group to match characters that are not a ]

- \\]\\]
    - Like the beginning, this matches ]]

## Parsing the Character: Dialog
![regex_problems](https://imgs.xkcd.com/comics/perl_problems_2x.png)

### pain: 1st attempt: `regex(r"{(?m)^(\w+):([^\n]*)}", multiline = TRUE)`

### Realization
Upon testing with sample data:
`" \"[[A boy sits in a barrel which is floating in an ocean.]]\\nBoy: I wonder where I'll float next?\\n[[The barrel drifts into the distance. Nothing else can be seen.]]\\n{{Alt: Don't we all.}}\""`
Upon doing a stringview, I noticed that "\n" was actually "\\n". Thus multiline regexes were useless!

### redemption
New regex: `str_match_all(test, r"{(?:\\n)?(\w+): ((?:.(?!\\n))+).\\n}")`

#### Regex negative lookahead

#### Non capturing groups
`(?:\\n)?(\w+): ((?:.(?!(?:\\n)?\w+:|\Z|\[|\{))*)(?:\\n\\?)*`

# Troublesome comics
785
992, 1286 - non parsable colons



```r
view_xkcd_string <- function(strin) {
    str_replace_all(strin, r"{\\n}", "\n") |> str_view()
}


scenebuilding = r"{\[\[([^\]]*)\]\]}"
dialog_regex = r"{(?:\\n)?([^:]+): ((?:.(?!\\n[^:]+:))*.)}"
# THIS IS THE NAME REGEX
names_regex = r"{(?:\\n)(?=(?:.(?!\\n))+:)([^:]+):}"
bad_newlines = r"{(?:\\n)(?!(?:.(?!\\n))+:)}"

parse_dialog <- function(dialog) {
    step0 = str_replace_all(dialog, r"{(?:\\n)+}", r"{\\n}")
    step1 = str_remove_all(step0, r"(^\s+"|\{\{.*\}\}"?$)")
    scene_info = str_extract_all(step1, scenebuilding)
    step2.1 = str_remove_all(step1, scenebuilding)
    step2.2 = str_replace_all(step2.1, r"{(?:\\n)+}", r"{\\n}")
    step2.3 = str_remove(step2.2, r"(\s*(?:\\n)+$)")
    names = str_match_all(step2.3, names_regex)
    dialog = str_split(step2.3, names_regex)
    n <- names |> map(\(x) reduce(x[,2], paste, .init="")) |> unlist()
    d <- dialog |> map(\(x) reduce(x, paste, .init="")) |> unlist()
    data.frame(names = n, dialog= d)
}
# sample <- xkcd |> sample_n(10) |> pull(transcript)
```



```r
xkcd_comma <- xkcd_date |> mutate(transcript = transcript |> str_replace_all("\\(COMMA\\)", ","))
# 
# mutate_and_parse = function(df) {
#     split_transcript = df$transcript |> parse_dialog() |> map(as.data.frame)
#     speakers = split_transcript |> map(\(x) reduce(x$V2, paste, .init = "")) |> unlist()
#     script = split_transcript |> map(\(x) reduce(x$V3, paste, .init = "")) |> unlist()
#     return(data.frame(speakers, script))
# }


xkcd_transcript <- xkcd_comma |> cbind(xkcd_comma |> pull(transcript) |> parse_dialog())
head(xkcd_transcript)
```

```
##   num       date weekday                   title              safe_title
## 1   1 2006-01-01     Sun       "Barrel - Part 1"       "Barrel - Part 1"
## 2   2 2006-01-01     Sun  "Petit Trees (sketch)"  "Petit Trees (sketch)"
## 3   3 2006-01-01     Sun       "Island (sketch)"       "Island (sketch)"
## 4   4 2006-01-01     Sun    "Landscape (sketch)"    "Landscape (sketch)"
## 5   5 2006-01-01     Sun           "Blown apart"           "Blown apart"
## 6   6 2006-01-01     Sun                 "Irony"                 "Irony"
##                                                                                                                                                                                                                                                                                                                                                                      transcript
## 1                                                                                                                                                                              "[[A boy sits in a barrel which is floating in an ocean.]]\\nBoy: I wonder where I'll float next?\\n[[The barrel drifts into the distance. Nothing else can be seen.]]\\n{{Alt: Don't we all.}}"
## 2                                                                                                                                                                                               "[[Two trees are growing on opposite sides of a sphere.]]\\n{{Alt-title: 'Petit' being a reference to Le Petit Prince, which I only thought about halfway through the sketch}}"
## 3                                                                                                                                                                                                                                                                                                                           "[[A sketch of an Island]]\\n{{Alt:Hello, island}}"
## 4                                                                                                                                                                                                                                                                    "[[A sketch of a landscape with sun on the horizon]]\\n{{Alt: There's a river flowing through the ocean}}"
## 5                                                                                                      "[[A black number 70 sees a red package.]]\\n70: hey, a package!\\n[[The package explodes with a <<BOOM>> and a red cloud of smoke.]]\\n[[There are a red 7, a green 5 and a blue 2 lying near a scorched mark on the floor.]]\\n{{alt text: Blown into prime factors}}"
## 6  "Narrator: When self-reference, irony, and meta-humor go too far\\nNarrator: A CAUTIONARY TALE\\nMan 1: This statement wouldn't be funny if not for irony!\\nMan 1: ha ha\\nMan 2: ha ha, I guess.\\nNarrator: 20,000 years later...\\n[[desolate badlands landscape with an imposing sun in the sky]]\\n{{It's commonly known that too much perspective can be a downer.}}"
##                                                                                                            alt
## 1                                                                                              "Don't we all."
## 2  "'Petit' being a reference to Le Petit Prince(COMMA) which I only thought about halfway through the sketch"
## 3                                                                                        "Hello(COMMA) island"
## 4                                                                  "There's a river flowing through the ocean"
## 5                                                                                   "Blown into prime factors"
## 6                                             "It's commonly known that too much perspective can be a downer."
##                                                         img link news
## 1     "https://imgs.xkcd.com/comics/barrel_cropped_(1).jpg"   NA   NA
## 2       "https://imgs.xkcd.com/comics/tree_cropped_(1).jpg"   NA   NA
## 3           "https://imgs.xkcd.com/comics/island_color.jpg"   NA   NA
## 4  "https://imgs.xkcd.com/comics/landscape_cropped_(1).jpg"   NA   NA
## 5       "https://imgs.xkcd.com/comics/blownapart_color.jpg"   NA   NA
## 6            "https://imgs.xkcd.com/comics/irony_color.jpg"   NA   NA
##   extra_parts                                names
## 1          NA                                  Boy
## 2          NA                                     
## 3          NA                                     
## 4          NA                                     
## 5          NA                                   70
## 6          NA  Narrator Man 1 Man 1 Man 2 Narrator
##                                                                                                                                                                                   dialog
## 1                                                                                                                                                        I wonder where I'll float next?
## 2                                                                                                                                                                                       
## 3                                                                                                                                                                                       
## 4                                                                                                                                                                                       
## 5                                                                                                                                                                        hey, a package!
## 6  Narrator: When self-reference, irony, and meta-humor go too far  A CAUTIONARY TALE  This statement wouldn't be funny if not for irony!  ha ha  ha ha, I guess.  20,000 years later...
```


# Analysis
## Dates

The first thing we can analyze without any data manipulation is the frequency of comics across each year and weekday.

```r
# we extract the year from the given date by using format(date), "%y"
xkcd_date |> mutate(year = format(date, "%Y")) |> ggplot(aes(year)) + geom_bar() + labs(title = "Number of Comics Posted by Year")
```

<img src="xkcd_files/figure-html/comicsByYear-1.png" width="672" />

```r
# graph for posts by day of the week
xkcd_date |> ggplot(aes(weekday)) + geom_bar() + labs(title = "Number of Comics Posted by Weekday")
```

<img src="xkcd_files/figure-html/comicsByWeekday-1.png" width="672" />

As we see, the yearly posts are pretty consistent. While 2024 provides no significance (as the year is not complete), 2006 does. We can investigate.

```r
xkcd_date |> filter(format(date, "%Y") == "2006") |> group_by(date) |> count() |> arrange(desc(n)) |> head()
```

```
## # A tibble: 6 × 2
## # Groups:   date [6]
##   date           n
##   <date>     <int>
## 1 2006-01-01    44
## 2 2006-09-20     2
## 3 2006-01-04     1
## 4 2006-01-06     1
## 5 2006-01-09     1
## 6 2006-01-12     1
```
We can see here that Munroe posted 44 comics on January 1, 2006. Which is the day xkcd was started. To quote Munroe at this time, "I was going through old math/sketching graph paper notebooks and didn't want to lose some of the work in them, so I started scanning pages. I took the more comic-y ones and put them up on a server I was testing out."

Now to discuss the second graph. While xkcd has had the majority of it's posts on MWF, there are some exceptions. We already know from the previous graph, that 44 comics were posted on 6-1-1, a sunday. Lets look at some of the other dates when this happened.

```r
xkcd_date_abnormal <- xkcd_date |> filter(weekday %in% c("Sun", "Tue", "Thu", "Sat"), date != "2006-01-01")
xkcd_date_abnormal |> group_by(weekday) |> count()
```

```
## # A tibble: 4 × 2
## # Groups:   weekday [4]
##   weekday     n
##   <ord>   <int>
## 1 Sun         3
## 2 Tue        16
## 3 Thu        12
## 4 Sat         3
```
So 3 of the sunday comics were not posted on the first day. Meaning we have 34 abnormal posts. Lets narrow down the time of theses abnormalities a bit further.

```r
xkcd_date_abnormal |> group_by(format(date, "%Y"), weekday) |> count()
```

```
## # A tibble: 25 × 3
## # Groups:   format(date, "%Y"), weekday [25]
##    `format(date, "%Y")` weekday     n
##    <chr>                <ord>   <int>
##  1 2006                 Sun         1
##  2 2006                 Tue         4
##  3 2006                 Thu         2
##  4 2006                 Sat         2
##  5 2007                 Tue         1
##  6 2007                 Thu         1
##  7 2008                 Tue         1
##  8 2008                 Thu         1
##  9 2009                 Tue         1
## 10 2009                 Thu         2
## # ℹ 15 more rows
```
It is not a surprise to see that the majority of date abnormalities are in 2006, when the comic was not full-time. For interest's sake, here are a few of the later comics which were abnormal.

```r
(xkcd_date_abnormal |> filter(format(date, "%Y") > 2018))[c(1:4, 8:10)]
```

```
##    num       date weekday                           title
## 1 2198 2019-09-03     Tue                         "Throw"
## 2 2289 2020-04-04     Sat                    "Scenario 4"
## 3 2300 2020-04-30     Thu  "Everyone's an Epidemiologist"
## 4 2445 2021-04-01     Thu                      "Checkbox"
## 5 2672 2022-09-13     Tue          "What If? 2 Flowchart"
##                                                               img
## 1                        "https://imgs.xkcd.com/comics/throw.png"
## 2                   "https://imgs.xkcd.com/comics/scenario_4.png"
## 3  "https://imgs.xkcd.com/comics/everyones_an_epidemiologist.png"
## 4                     "https://imgs.xkcd.com/comics/checkbox.gif"
## 5          "https://imgs.xkcd.com/comics/what_if_2_flowchart.png"
##                            link
## 1                            NA
## 2                            NA
## 3                            NA
## 4                            NA
## 5  "https://xkcd.com/what-if-2"
##                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     news
## 1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     NA
## 2                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     NA
## 3                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     NA
## 4  "<br />This comic was put together by <a href="https://chromakode.com/">Max Goodhart</a>(COMMA) <a href="https://twitter.com/fadinginterest">Patrick</a>(COMMA) <a href="https://twitter.com/Aiiane">Amber</a>(COMMA) <a href="https://twitter.com/bstaffin">Benjamin Staffin</a>(COMMA) <a href="https://twitter.com/cotrone">Kevin Cotrone</a>(COMMA) <a href="https://twitter.com/wirehead2501">Kat</a>(COMMA) and <a href="https://twitter.com/dyfrgi">Michael Leuchtenburg</a>."
## 5                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     NA
```
<p float="left">
    <img src="https://imgs.xkcd.com/comics/throw.png" alt="throw" width="19%"/>
    <img src="https://imgs.xkcd.com/comics/scenario_4.png" alt="scenario_4" width="19%"/>
    <img src="https://imgs.xkcd.com/comics/everyones_an_epidemiologist.png" alt="everyones_an_epidemiologist" width="19%"/>
    <img src="https://imgs.xkcd.com/comics/checkbox.gif"alt="checkbox" width="19%"/>
    <img src="https://imgs.xkcd.com/comics/what_if_2_flowchart.png" alt="What if 2 flowchart" width="19%"/>
</p> 
Interestingly enough, all but one of the last 5 comics which were off-schedule were "special" comics (a term we will define later) and/or promotions for Munroe's most recent publication (in these cases, <ins>What if? 2</ins> and <ins>How to</ins> where promoted).

## Special comics

Speaking of special comics. Lets look at some of those. In this project, we define special comics as any unusual post that isn't just a comic. The primary form of this are posts where the extra_parts fields are not null, that is the comic is an interactive comic. It could be a game, a gif, or a movie. We will also be looking at comics with links and comics where some news was announced. 

```r
specialComics <- xkcd_date |> filter(extra_parts != " NA")
hasNews <- xkcd_date |> filter(news != " NA")
hasLink <- xkcd_date |> filter(link != " NA")
special_union <- union(union(specialComics, hasNews), hasLink)
nrow(specialComics)
```

```
## [1] 23
```

```r
nrow(hasNews)
```

```
## [1] 54
```

```r
nrow(hasLink)
```

```
## [1] 72
```

```r
nrow(special_union)
```

```
## [1] 125
```

```r
nrow(intersect(specialComics, hasNews))
```

```
## [1] 9
```

```r
nrow(intersect(specialComics, hasLink))
```

```
## [1] 3
```

```r
nrow(intersect(hasNews, hasLink))
```

```
## [1] 12
```

```r
nrow(intersect(specialComics, intersect(hasNews, hasLink)))
```

```
## [1] 0
```

So there are 23 special comics. 54 comics with news announced, and 72 comics which have a link attached to the picture. This totals to 125 special comics (as some comics fall under more than one of the 3 categories). We see that there are 9 comics which are both special and have news, 3 comics which are special and have a link, 12 comics which have both news and a link, and 0 comics with all 3 qualities.

Lets look at how frequent these comics were over time.


```r
special_union |> mutate(year = format(date, "%Y")) |> ggplot(aes(year)) + geom_bar() + labs(title = "Comics with Unique Properties by Year")
```

<img src="xkcd_files/figure-html/unnamed-chunk-2-1.png" width="672" />

```r
specialComics |> mutate(year = format(date, "%Y")) |> ggplot(aes(year)) + geom_bar() + labs(title = "Special Comics by Year")
hasLink |> mutate(year = format(date, "%Y")) |> ggplot(aes(year)) + geom_bar() + labs(title = "Comics with Links by Year")
hasNews |> mutate(year = format(date, "%Y")) |> ggplot(aes(year)) + geom_bar() + labs(title = "Comics with News by Year")
```

<img src="xkcd_files/figure-html/figures-side-1.png" width="33%" /><img src="xkcd_files/figure-html/figures-side-2.png" width="33%" /><img src="xkcd_files/figure-html/figures-side-3.png" width="33%" />
We see here that the majority of the comics with extra features peaked around 2012, and had a spike in 2022. This is true for the individual properties as well, with the exception that news did not have a spike in 2022.

Lets go back a bit to where we analyzed the comics that were posted on Tuesdays and Thursdays. We can try to prove our hypothesis that most of these are our special comics. 

```r
special_union |> ggplot(aes(weekday)) + geom_bar() + labs(title = "Comics with Unique Properties by Weekday")
```

<img src="xkcd_files/figure-html/unnamed-chunk-3-1.png" width="672" />

```r
nrow(union(special_union, xkcd_date_abnormal))
```

```
## [1] 145
```

```r
nrow(intersect(special_union, xkcd_date_abnormal)) / nrow(xkcd_date_abnormal)
```

```
## [1] 0.4117647
```

```r
nrow(special_union) / nrow(xkcd)
```

```
## [1] 0.04270584
```
We see here that the distribution looks fairly similar to the previous weekday graph. However looking at the numbers, we see that there are 145 comics with unique properties that were posted on abnormal days. That's 41.1% of all comics posted on abnormal days. Considering comics with unique properties make up about 4.3% of all comics. This means unique comics make up a significant portion of comics posted on off-days.

## Titles
One thing mentioned in Section 1: The Data is that there didn't seem to be a difference between 'title' and 'safe_title'. Let's look at that now.


```r
xkcd_title_diff <- xkcd_date |> filter(title != safe_title)
xkcd_title_diff[1:5]
```

```
##   num       date weekday
## 1 259 2007-05-09     Wed
## 2 472 2008-09-05     Fri
##                                                      title           safe_title
## 1                               "Clich&eacute;d Exchanges"   "Clichd Exchanges"
## 2  "<span style="color: #0000ED">House</span> of Pancakes"  "House of Pancakes"
```
One of these comics has an accent above the 'e' in the word 'Clichéd' which may not be readable by some browsers. The other has a blue fill for the word 'House', which once again, may not be readable by some browsers. It is interesting that the answer for this problem was to create an entire new field for this problem, when it could have been handled like the 'extra_parts' item, where only some of the comics even register one (we put in a NA value for all comics which had no 'extra_parts' attribute).
<p float="left">
    <img src="https://imgs.xkcd.com/comics/cliched_exchanges.png" alt="cliched_exchanges" width="49%"/>
    <img src="https://imgs.xkcd.com/comics/house_of_pancakes.png" alt="house_of_pancakes" width="49%"/>
</p> 

## The transcript
Now for the part we've all been waiting for. After expending much effort into parsing the transcript with regular expressions, we will finally use it. Starting with the most common 100 words used in his comic.


```r
xkcd_words <- xkcd_transcript |> separate_longer_delim(transcript, delim = regex(r"(\s+)")) |> mutate(transcript = tolower(transcript) |> str_replace_all("[^[\\w+]]", "") |> na_if("")) |> filter(!is.na(transcript))
word_frequency <- xkcd_words |> group_by(transcript) |> count() |> arrange(desc(n))
word_frequency
```

```
## # A tibble: 31,430 × 2
## # Groups:   transcript [31,430]
##    transcript     n
##    <chr>      <int>
##  1 the         9333
##  2 a           7204
##  3 of          4135
##  4 to          4092
##  5 and         3547
##  6 is          3298
##  7 in          2887
##  8 i           2367
##  9 you         2030
## 10 on          1956
## # ℹ 31,420 more rows
```



To no one's suprise, the most common words are the articles 'the', 'a', 'of', etc.. However ...

Let's now look at the most common character's in the comic.


# Sources

- xkcd.com
- xkcd.com/json.html
- xkcd.com/about/
- explainxkcd.com