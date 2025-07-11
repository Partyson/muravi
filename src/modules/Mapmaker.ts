import type { CanvasArtist } from "./Artist";
import type { IArena } from "./Requester/DTO";

// класс-картограф, наносит на карту объекты
export class Mapmaker {
    artist: CanvasArtist;
    constructor(artist: CanvasArtist) {
        this.artist = artist;
    }

    public map(arena: IArena) {
        for (let gex of arena.map) {
            this.artist.drawGex(gex.q, gex.r, gex);
        }
        this.artist.drawHome(arena.home);
        for (let ant of arena.ants) {
            this.artist.drawAnt(ant.q, ant.r, ant);
        }
        for (let enemy of arena.enemies) {
            this.artist.drawAnt(enemy.q, enemy.r, enemy, true);
        }
        for (let food of arena.food) {
            this.artist.drawFood(food.q, food.r, food);
        }
    }
}
