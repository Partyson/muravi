import type { CanvasArtist } from "./Artist";
import { COLORS } from "./Artist/Colors";
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
        for (let ant of arena.ants) {
            if (ant.move) {
                this.artist.drawArrow(ant.q, ant.r, ant.move, COLORS.arrow);
            }
        }
    }

    public translateToMap(arena: IArena) {
        const [x, y] = this.artist.getCanvasCoords(
            arena.home[0].r,
            arena.home[0].q
        );
        this.artist.goTo(
            -x + this.artist.canvas.width / 2 / this.artist.scale,
            -y + this.artist.canvas.height / 2 / this.artist.scale
        );
    }
}
