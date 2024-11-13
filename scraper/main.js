// scrape from all these pages https://remywiki.com/Category:DanceDanceRevolution_Songs

const axios = require('axios')
const cheerio = require('cheerio')

function parseRuntime(time){
    const arr = time.split(":")
    return parseInt(arr[1])*60 + parseInt(arr[2])
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
                obj.runtime = parseRuntime(element)
        });
        obj.playable = true;
        obj.licensed = false;
        $('.mw-normal-catlinks ul li a').each((index, element) => {
            const t = $(element).text()
            if(t.includes("DanceDanceRevolution Cut Songs")){
                obj.playable =false;
            }
            if (t.includes("DanceDanceRevolution Licensed Songs")){
                obj.licensed = true;
            }
        });
        
        console.log(obj)
        return obj
    } catch(e) {
        console.error(e)
    }
}

fetch_page("https://remywiki.com/Scarlet_keisatsu_no_ghetto_patrol_24_ji");