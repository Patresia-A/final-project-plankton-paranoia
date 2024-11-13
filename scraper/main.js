
const axios = require("axios");
const cheerio = require("cheerio");
const chronoGames = require("./chronologically-sorted-games")
const hepburn = require("hepburn")
const wanakana = require('wanakana');

const oldRatedGames = chronoGames.splice(0, 15)
const newRatedGames = chronoGames.splice(-10)

function removeNonAscii(string){
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
        song.songName = $(".mw-page-title-main").text();

        const songInfo = $(".mw-parser-output p").first().text().split("\n");

        //parsing description area
        let hasGame = false
        songInfo.forEach((element) => {
            if (element.includes("BPM")) {
                const bpmObj = parseBPM(element.split(": ")[1]);
                song.lowerBPM = parseInt(bpmObj.lower);
                song.higherBPM = parseInt(bpmObj.higher);
                song.changingBPM = bpmObj.lower != bpmObj.higher
            }
            else if (element.includes("Artist")) {
                let artist = element.split(':').slice(1).join(':').trim();
                //attempt to handle japanese words
                if (hepburn.containsKana(artist))
                    artist = wanakana.toRomaji(artist)
                //remove all non-ascii
                artist = removeNonAscii(artist)
                song.artist = artist
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


        //determining cut and licensed status 
        song.playable = true;
        song.licensed = false;
        $(".mw-normal-catlinks ul li a").each((index, element) => {
            const t = $(element).text();
            if (t.includes("DanceDanceRevolution Cut Songs")) {
                song.playable = false;
            }
            if (t.includes("DanceDanceRevolution Licensed Songs")) {
                song.licensed = true;
            }
        });
        if (song.playable) {
            song.isNewRated = true;
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
                    // console.log(cell).text().trim()
                    rowData.push($(cell).text().trim());
                });
                if (rowData.length != 0)
                    difficultyRows.push(rowData);
            });
    // attempt to handle case like in https://remywiki.com/Acid,Tribal_%26_Dance_(DDR_EDITION), where it just says difficulty and notecounts
    //CURRENTLY NOT WORKING!!!!!!!!!!
        if (difficultyClasses.length === 0){
            $('h2:has(.mw-headline)')
            .next('table')
            .find('tbody tr')
            .eq(1)
            .find('th')
            .each((i, cell) => {
                difficultyClasses.push($(cell).text().trim());
            });
            $('h2:has(.mw-headline)')
            .next('table')
            .find('tbody tr')
            .each((i, row) => {
                const rowData = [];
                $(row).find('td').each((j, cell) => {
                    console.log$(cell).text().trim()
                    rowData.push($(cell).text().trim());
                });
                if (rowData.length != 0)
                    difficultyRows.push(rowData);
            });
        }

        charts = []

        let currentRatingRowIndex = 0;
        song.isNewRated = false;

        //determining most recent  game rating
        for (let i = 1; i < difficultyRows.length; i++) {
            const gameName = difficultyRows[i][0]
            if (gameName.includes("Present")) {
                currentRatingRowIndex = i;
                song.isNewRated = true;
                break;
            }
        }
        //case where present is not found
        //I can't find a great way to determine the most recent ratings for a song which has been removed.... I will just suffer
        if (currentRatingRowIndex === 0) {
            currentRatingRowIndex = 1
        }

        //determining newrating status
        // if (!isNewRated){

        //     for (let i = 1; i < difficultyRows.length; i++) {
        //         if (!isNewRated) {
        //             for (let j = 0; j < newRatedGames.length; j++) {
        //                 if (newRatedGames[j].includes(difficultyRows[i][0])) {
        //                     song.isNewRated = true;
        //                 }
        //             }
        //         }
        //     }
        // }
        let isDoubles = false;

        console.log(difficultyClasses)
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
                console.log("hi")
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
        console.log(difficultyRows)
        song.charts = charts;
        console.log(song);
        return song;
    } catch (e) {
        console.error(e);
    }
}

parse_page("https://remywiki.com/Right_on_time_(Ryu_Remix)")