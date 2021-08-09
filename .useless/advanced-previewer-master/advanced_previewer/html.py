# -*- coding: utf-8 -*-

"""
This file is part of the Advanced Previewer add-on for Anki

HTML/CSS/JS boilerplate used by the previewer

Copyright: Glutanimate 2016-2017
License: GNU AGPL, version 3 or later; https://www.gnu.org/licenses/agpl-3.0.en.html
"""

# General preview window styling
preview_css = """
body{
    // body css here
}
"""

# Styling used when previewing multiple cards
multi_preview_css = """
/*Card styling*/
.card{
    margin-top: 0.5em;
    margin-bottom: 0.5em;
    padding-top: 0.5em;
    padding-bottom: 0.5em;
    border-style: solid;
    border-color: #EFEFEF;
    cursor: pointer;
    background-color: #FFFFFF;
}

/*Styling to apply when hovering over cards*/
.card:hover{
    background-color: #F9FFE0;
}

/*Styling to apply when card is selected*/
.card.active{
    background-color: #EFEFEF;
}
"""

# JS function that applies active styling to selected card
multi_preview_js = """
function toggleActive(elm) {
    otherElms = document.getElementsByClassName("card");
    for (var i = 0; i < otherElms.length; i++) {
        otherElms[i].classList.remove("active");
    }
    elm.classList.add("active")
}
"""
