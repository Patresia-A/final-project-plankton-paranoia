
const axios = require("axios");
const cheerio = require("cheerio");
const chronoGames = require("./chronologically-sorted-games")
const hepburn = require("hepburn")
const wanakana = require('wanakana');

const oldRatedGames = chronoGames.splice(0, 15)
const newRatedGames = chronoGames.splice(-10)

function removeNonAscii(string) {
    return string.replace(/[^\x00-\x7F]/g, "");
}
//romanizes a string, then removes all non-ascii
function asciiNormalize(string){
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
        const response = await axios.get(page);
        const html = response.data;
        const $ = cheerio.load(html);
        const song = {};

        song.licensed = false;
        let isCutSong = false;
        $(".mw-normal-catlinks ul li a").each((index, element) => {
            const t = $(element).text();
            // we only want playable songs! exit if song has been cut
            if (t.includes("DanceDanceRevolution Cut Songs")) {
                isCutSong = true;
                return null;
            }
            if (t.includes("DanceDanceRevolution Licensed Songs")) {
                song.licensed = true;
            }
        });
        
        if (isCutSong) return null;

        song.songName = asciiNormalize($(".mw-page-title-main").text());

        const songInfo = $(".mw-parser-output p").first().text().split("\n");

        let hasGame = false
        songInfo.forEach((element) => {
            if (element.includes("BPM")) {
                const bpmObj = parseBPM(element.split(": ")[1]);
                song.lowerBPM = parseInt(bpmObj.lower);
                song.higherBPM = parseInt(bpmObj.higher);
                song.changingBPM = bpmObj.lower != bpmObj.higher
            }
            else if (element.includes("Artist")) {
                song.artist = asciiNormalize(element.split(':').slice(1).join(':').trim())
            }

            else if (element.includes("Length")) song.runtime = parseRuntime(element);

            else if (!hasGame && element.includes("First Music Game Appearance: DanceDance")) {
                song.game = element.split(": ")[1];
                hasGame = true;
            }
            else if (!hasGame) {
                $('.mw-parser-output > ul').first().find('li').each((i, e) => {
                    const text = $(e).text().trim();
                    if (text.includes('Dance')) {
                        song.game = text;
                        hasGame = true;
                        return false;
                    }
                });

            }
        });

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
                    // console.log(cell).text().trim()
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
        console.log(song);
        return song;
    } catch (e) {
        console.error(e);
    }
}

parse_page("https://remywiki.com/Scarlet_keisatsu_no_ghetto_patrol_24_ji")
parse_page("https://remywiki.com/Acid,Tribal_%26_Dance_(DDR_EDITION)")
parse_page("https://remywiki.com/17_sai")