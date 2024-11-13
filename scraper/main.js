// scrape from all these pages https://remywiki.com/Category:DanceDanceRevolution_Songs

const axios = require('axios')
const cheerio = require('cheerio')

function parseRuntime(time){
    const arr = time.split(":")
}
function parseBPM(bpm){
    const arr = bpm.split("-")
    if (bpm.includes("-")){
        return {
            lower: arr[0],
            higher: arr[1]
        }
    } else {
        return {
            lower: arr[0],
            higher: arr[0]
        }
    }
}
async function fetch_page(page){
    try {
        const response = await axios.get(page);
        const html = response.data;
        const $ = cheerio.load(html);
        const obj = {}
        obj.songName = $('.mw-page-title-main').text();

        const songInfo = $('.mw-parser-output p').first().text().split('\n');
        songInfo.forEach(element => {
            if (element.includes("Artist"))
                obj.artist = element.split(": ")[1];
            if (element.includes("BPM")){
                const bpmObj = parseBPM(element.split(": ")[1])
                obj.lowerBPM = bpmObj.lower;
                obj.higherBPM = bpmObj.higher;
            }
            if (element.includes("Length"))
                obj.runtime 
        });
        console.log(obj)
        return obj
    } catch(e) {
        console.error(e)
    }
}

fetch_page("https://remywiki.com/Acid,Tribal_%26_Dance_(DDR_EDITION)");