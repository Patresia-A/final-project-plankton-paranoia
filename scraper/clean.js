const fs = require('fs');
const { forEach } = require('./chronologically-sorted-games');
const chronoGames = require("./chronologically-sorted-games");


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
const validDifficulties = [
    "beginner",
    "Beginner",
    "BEGINNER",
    "Basic",
    "basic",
    "BASIC",
    "difficult",
    "Difficult",
    "DIFFICULT",
    "expert",
    "Expert",
    "EXPERT",
    "Challenge",
    "challenge",
    "CHALLENGE"
]
function isFaultySong(song){
    let flag = false
    if (!song.songName || !song.artist || !song.lowerBPM || !song.higherBPM || !song.runtime || !song.charts){
        console.log(`null category for song ${song.songName}`)
        flag = true
    }
    if (!chronoGames.includes(song.game))
    {
        console.log(`bad game for song ${song.songName}`)
        flag = true
    }
    if (song.charts.length > 10){
        console.log(`too many charts for song ${song.songName}`)
        flag = true
    }
    song.charts.forEach((chart) => {
        //no current ddr chart has more than 1000 notes, max 360 has 1000
        if (chart.notes > 1000){
            console.log(`too many notes in chart for song ${song.songName}`)
            flag = true
        }
        if (!validDifficulties.includes(chart.difficulty)){
            console.log(`invalid difficulty in chart for song ${song.songName}`)
            flag = true
        }
        // if (!chart.difficultyRating && chart.notes && chart.notes !== 0)
        // {
        //     console.log(`invalid difficulty rating for ${chart.difficulty} for song ${song.songName}`)
        //     flag = true
        // }
        if (chart.difficultyrating){
            console.log(`improperly named difficulty rating for ${song.songName} chart ${chart.difficulty}`)
            flag = true
        }
    })
    return flag
    
}
function verify(songs){
    faultySongs = []
    count = 0
    songs.forEach((song) => {
        count = isFaultySong(song) ? count + 1 : count
    })
    console.log(`Detected ${count} faulty songs`)
}


const filePath = './clean.json';

const songs = readJsonFile(filePath);

verify(songs)


// if (songs) {
//     for (let i = 0; i < songs.length; i++) {
//         for (let j = 1; j < chronoGames.length; j++) {
//             if (songs[i].game === chronoGames[j])
//                 break;
//             if (songs[i].game.includes(chronoGames[j])) {
//                 songs[i].game = chronoGames[j]
//                 break
//             }
//             if (j === chronoGames.length && !songs[i].game.includes(chronoGames[j]))
//                 songs[i].game = ""
//         }
//     }

//     const fs = require("fs")
//     fs.writeFile("clean.json", JSON.stringify(songs), (e) => {
//         if (e) throw e
//     })
// }
