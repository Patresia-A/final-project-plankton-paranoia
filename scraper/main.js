
const axios =require("axios");
const cheerio = require("cheerio");
const chronoGames = require("./chronologically-sorted-games")
const hepburn = require("hepburn")
const wanakana = require('wanakana');

function removeNonAscii(string) {
    return string.replace(/[^\x00-\x7F]/g, "");
}
//romanizes a string, then removes all non-ascii
function asciiNormalize(string) {
    if (hepburn.containsKana(string))
        string = wanakana.toRomaji(string)
    return string.replace(/[^\x00-\x7F]/g, "");
}
// scrape from all these pages https://remywiki.com/Category:DanceDanceRevolution_Songs
function parseRuntime(time) {
    const arr = time.split(":");
    return parseInt(arr[1]) * 60 + parseInt(arr[2]);
}
function parseBPM(bpm) {
    const arr = bpm.split("-");
    if (bpm.includes("-")) {
        return {
            lower: arr[0],
            //we do this split nonsense because sometimes the BPM might have more info after the number, for an example see https://remywiki.com/MAX_360 
            higher: arr[1].split(" ")[0],
        };
    } else {
        return {
            lower: arr[0],
            higher: arr[0].split(" ")[0],
        };
    }
}


async function parse_page(page) {
    try {
        console.log("processing page: " + page)
        const response = await axios.get(page);
        const $ = cheerio.load(response.data);
        const song = {};

        song.licensed = false;
        $(".mw-normal-catlinks ul li a").each((index, element) => {
            const t = $(element).text();
            // we only want playable songs! exit if song has been cut
            if (t.includes("DanceDanceRevolution Cut Songs") || t.includes("DanceDanceRevolution CS Exclusives")) {
                song.isInvalid = true;
                return null;
            }
            if (t.includes("DanceDanceRevolution Licensed Songs")) {
                song.licensed = true;
            }
        });

        if (song.isInvalid) return null;

        song.songName = asciiNormalize($(".mw-page-title-main").text());

        const songInfo = $('div.mw-parser-output > div.thumb.tright').nextAll('p').first().text().split("\n");


        songInfo.forEach((element) => {
            if (!song.lowerBPM && element.includes("BPM")) {
                const bpmObj = parseBPM(element.split(": ")[1]);
                song.lowerBPM = parseInt(bpmObj.lower);
                song.higherBPM = parseInt(bpmObj.higher);
                song.changingBPM = bpmObj.lower != bpmObj.higher
            }
            else if (!song.artist && element.includes("Artist")) {
                song.artist = asciiNormalize(element.split(':').slice(1).join(':').trim())
            }

            else if (!song.runtime && element.includes("Length")) song.runtime = parseRuntime(element);
            else if (!song.game && element.includes("DanceDanceRevolution"))
                chronoGames.forEach((game) => {
                    if (element === game)
                        song.game = element.split(": ")[1];
                })

        });
        //case where game is contained in a <li>
        if (!song.game) {
            const listsAfterParagraph = $('div.mw-parser-output > div.thumb.tright')
                .nextAll('p')
                .first()
                .nextAll('ul, ol').
                first().each((i, list) => {
                    $(list).find('li').map((j, li) => $(li).text().trim()).get().forEach((item) => {
                        if (song.game) return;
                        if (item.includes("DanceDanceRevolution")) {
                            song.game = item;
                            return;
                        }
                    })
                })
        }
        if (!song.game) {
            return null;
        }

        //difficulty class meaning "expert", "challenge", "beginner"
        const difficultyClasses = [];
        $('h3:has(.mw-headline#DanceDanceRevolution)')
            .next('table')
            .find('tbody tr')
            .eq(1)
            .find('th')
            .each((i, cell) => {
                difficultyClasses.push($(cell).text().trim());
            });

        // the rows of raw data containing difficulties and notecounts
        const difficultyRows = []
        $('h3:has(.mw-headline#DanceDanceRevolution)')
            .next('table')
            .find('tbody tr')
            .each((i, row) => {
                const rowData = [];
                $(row).find('td').each((j, cell) => {
                    rowData.push($(cell).text().trim());
                });
                if (rowData.length !== 0)
                    difficultyRows.push(rowData);
            });

        // attempt to handle case like in https://remywiki.com/Acid,Tribal_%26_Dance_(DDR_EDITION), where it just says difficulty and notecounts
        if (difficultyClasses.length === 0) {
            $('table.wikitable tbody tr').eq(1).find('th').each((i, row) => {
                difficultyClasses.push($(row).text().trim());
            });

            $('table.wikitable td')
            $('table.wikitable tbody tr').each((i, row) => {
                const rowData = [];
                $(row).find('td').each((j, cell) => {
                    rowData.push($(cell).text().trim());
                });
                if (rowData.length !== 0)
                    difficultyRows.push(rowData);
            })
        }

        charts = []
        let currentRatingRowIndex = 0;
        //determining most up to date rating rating
        for (let i = 1; i < difficultyRows.length; i++) {
            if (difficultyRows[i][0].includes("Present")) {
                currentRatingRowIndex = i;
                break;
            }
        }
        let isDoubles = false;

        for (let i = 0; i < difficultyClasses.length; i++) {
            //parsing if chart is a doubles chart...
            if (isDoubles || i > 5 || ((difficultyClasses[i] === "Beginner" || difficultyClasses[i] === "Basic" || difficultyClasses[i] === "Difficult") &&
                (difficultyClasses[i - 1] === "Expert" || difficultyClasses[i - 1] === "Challenge"))) {
                isDoubles = true;
            }

            const noteArr = difficultyRows[0][i + 1].split("/")

            //Notecount might be split in two ways... either "680 / 4" or "948 / 9 / 0".. thus we must handle shocks differently
            let shockNotes = 0;
            if (noteArr.length === 3) {
                shockNotes = parseInt(noteArr[2])
            }
            charts.push(
                {
                    "difficulty": difficultyClasses[i],
                    "isDoubles": isDoubles,
                    "notes": parseInt(noteArr[0]),
                    "freezeNotes": parseInt(noteArr[1]),
                    "shockNotes": shockNotes,
                    "difficultyRating": parseInt(removeNonAscii(difficultyRows[currentRatingRowIndex][i + 1]))
                }
            )
        }
        song.charts = charts;
        return song;
    } catch (e) {
        console.error(e);
        return e;
    }
}




const baseURL = "https://remywiki.com"
const songLinks = []
async function getPageURLs(page) {
    console.log("reading from page " + baseURL + page)
    const response = await axios.get(baseURL + page);
    const $ = cheerio.load(response.data);

    $('div.mw-category-group a').each((i, element) => {
        const href = $(element).attr('href');
        if (!href.includes("Category")) {
            songLinks.push(href)
        }
    });


    const nextPageHref = $('a')
        .filter((i, el) => $(el).text().trim() === 'next page')
        .attr('href');
    if (nextPageHref)
        await getPageURLs(nextPageHref)
    else
        return "ok!"
}
async function getSongs(firstPage) {
    songs = []
    await getPageURLs(firstPage)
    //    for(let i = 0; i < 30; i++){
    //         song = await parse_page(baseURL + songLinks[i])
    //         if(song)
    //         songs.push(song)
    //    }
    //    for production
    for (let i = 0; i < songLinks.length; i++) {
        song = await parse_page(baseURL + songLinks[i])
        if (song)
            songs.push(song)
    }
    return songs;
}

const fs = require("fs")
getSongs("/Category:DanceDanceRevolution_Songs").then((res) => {
    console.log("Writing songs")
    fs.writeFile("songs.json", JSON.stringify(res), (e) => {
        if (e) throw e
    })
})
