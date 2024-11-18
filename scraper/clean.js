const fs = require('fs');
const { forEach } = require('./chronologically-sorted-games');
const chronoGames = require("./chronologically-sorted-games")


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


const filePath = './songs.json';

const songs = readJsonFile(filePath);

if (songs) {
    for (let i = 0; i < songs.length; i++) {
        for (let j = 1; j < chronoGames.length; j++) {
            if (songs[i].game === chronoGames[j])
                break;
            if (songs[i].game.includes(chronoGames[j])) {
                songs[i].game = chronoGames[j]
                break
            }
            if (j === chronoGames.length && !songs[i].game.includes(chronoGames[j]))
                songs[i].game = ""
        }
    }

    const fs = require("fs")
    fs.writeFile("clean.json", JSON.stringify(songs), (e) => {
        if (e) throw e
    })
}
