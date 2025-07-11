import { CanvasArtist } from "./modules/Artist";
import { Mapmaker } from "./modules/Mapmaker";
import { Requester } from "./modules/Requester";

// html-код на страницу
document.querySelector<HTMLDivElement>("#app")!.innerHTML = `
  <canvas style="border: 1px solid red;" id="canvas" width="4000" height="4000"></canvas>
`;

const artist = new CanvasArtist(
    document.getElementById("canvas") as HTMLCanvasElement,
    30
);
const requester = new Requester(
    "https://games-test.datsteam.dev",
    import.meta.env.VITE_TOKEN
);
const mapper = new Mapmaker(artist);

// метод рендера кадра
const renderFrame = async () => {
    const arena = await requester.requestArena();
    mapper.map(arena);
};

setInterval(renderFrame, 4000)

