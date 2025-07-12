import { CanvasArtist } from "./modules/Artist";
import { Mapmaker } from "./modules/Mapmaker";
import { Requester } from "./modules/Requester";
import type { IArena } from "./modules/Requester/DTO";

const artist = new CanvasArtist(
    document.getElementById("canvas") as HTMLCanvasElement,
    8
);
const requester = new Requester(
    "https://games-test.datsteam.dev",
    import.meta.env.VITE_TOKEN
);
const mapper = new Mapmaker(artist);

document.addEventListener("keydown", (event) => {
    switch (event.key) {
        case "q":
            artist.zoom(1);
            break;
        case "e":
            artist.zoom(-1);
            break;
        case "a":
            artist.move(artist.hexagoneRadius, 0);
            break;
        case "d":
            artist.move(-artist.hexagoneRadius, 0);
            break;
        case "w":
            artist.move(0, artist.hexagoneRadius);
            break;
        case "s":
            artist.move(0, -artist.hexagoneRadius);
            break;
        default:
            break;
    }
    renderFrame();
});

let lastArena: IArena;
let renderedFrames = 0;
// метод рендера кадра
const renderFrame = async () => {
    artist.clear();
    if (renderedFrames === 0) {
        console.log("go to map");
        mapper.translateToMap(lastArena)
    }
    mapper.map(lastArena);
    renderedFrames += 1;
};

setInterval(async () => {
    const arena = await requester.requestArena();
    lastArena = arena;
    renderFrame();
}, 2000);
