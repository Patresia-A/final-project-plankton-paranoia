// scrape from all these pages https://remywiki.com/Category:DanceDanceRevolution_Songs

const axios = require("axios");
const cheerio = require("cheerio");

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
async function fetch_page(page) {
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
            else if (element.includes("Artist")) song.artist = element.split(':').slice(1).join(':').trim();

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
                if (rowData.length != 0)
                    difficultyRows.push(rowData);
            });

        charts = []
        let isDoubles = false;
        for (let i = 0; i < difficultyClasses.length; i++) {
            //parsing if chart is a doubles chart...
            if (isDoubles || i > 5 || ((difficultyClasses[i] === "Beginner" || difficultyClasses[i] === "Basic" || difficultyClasses[i]=== "Difficult") && 
                (difficultyClasses[i - 1] === "Expert" || difficultyClasses[i - 1] === "Challenge"))){
                    isDoubles = true;
            }
            const noteArr = difficultyRows[0][i+1].split("/")
            
            //Notecount might be split in two ways... either "680 / 4" or "948 / 9 / 0".. thus we must handle shocks differently
            let shockNotes = 0;
            if (difficultyRows.length === 2){
                shockNotes = parseInt(noteArr[2])
            }

            charts.push(
                {
                    "difficulty": difficultyClasses[i],
                    "isDoubles": isDoubles,
                    "notes": parseInt(noteArr[0]),
                    "freezeNotes": parseInt(noteArr[1]),
                    "shockNotes": shockNotes
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

fetch_page("https://remywiki.com/Scarlet_keisatsu_no_ghetto_patrol_24_ji");
