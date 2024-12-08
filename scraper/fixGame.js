// I accidentally corrected all songs from DDR A - A20 PLUS to just be DDR A
const fs = require("fs")
const axios =require("axios");
const cheerio = require("cheerio");

function readJsonFile(filePath) {
    try {
        const jsonData = fs.readFileSync(filePath, 'utf-8');
        const jsObjects = JSON.parse(jsonData);

        return jsObjects;
    } catch (error) {
        console.error("Error reading or parsing the JSON file:", error.message);
        return null;
    }
}
const currentSongs = readJsonFile("clean.json")

// console.log(songs)
let i = 0;
targetGames = [    
    "DanceDanceRevolution A",
    "DanceDanceRevolution A20",
    "DanceDanceRevolution A20 PLUS",
    "DanceDanceRevolution A3",
]

async function fix_game(page) {
    const response = await axios.get(page);
    const $ = cheerio.load(response.data);
    const songName = $(".mw-page-title-main").text();
    for (let i = 0; i < currentSongs.length; i++){
        if (currentSongs[i].songName === songName){
            if (currentSongs[i].game === "DanceDanceRevolution A" ){
                console.log(`Fixing ${songName}`)
                const trueGame = $('a').filter((_, el) => {
                    const text = $(el).text();
                    return targetGames.includes(text);
                }).first().text()
                currentSongs[i].game = trueGame
            }
            break;
        }
        if (currentSongs[i].songName.toString() > songName ){
            console.log (`Possible incorrect song name for ${songName}`)
            break;
        }
    }
}

const songLinks = []
const baseURL = "https://remywiki.com"

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

    for (let i = 0; i < songLinks.length; i++) {
        song = await fix_game(baseURL + songLinks[i])
        if (song)
            songs.push(song)
    }
    return songs;
}


getSongs("/Category:DanceDanceRevolution_Songs").then((res) => {
    console.log("Writing songs")
    fs.writeFile("fixed_final.json", JSON.stringify(currentSongs), (e) => {
        if (e) throw e
    })
})
