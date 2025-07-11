import { Colorist } from "./Colorist";
import type { IArena } from "./Requester/DTO";
import type { IAnt, IEnemyAnt } from "./Requester/Entities/Ant";
import type { IFood } from "./Requester/Entities/Food";
import type { IGex } from "./Requester/Entities/Gex";

// класс, который рисует
export class CanvasArtist {
    private canvas: HTMLCanvasElement;
    private ctx: CanvasRenderingContext2D;
    private hexagoneRadius: number;
    private hexagoneP: number;
    constructor(canvas: HTMLCanvasElement, hexagoneRadius: number = 20) {
        this.canvas = canvas;
        this.ctx = canvas.getContext("2d") as CanvasRenderingContext2D;
        this.hexagoneRadius = hexagoneRadius;
        // длина перпендикуляра из центра к стороне
        this.hexagoneP = hexagoneRadius * (Math.sqrt(3) / 2);
    }

    private getCanvasCoords(posr: number, posq: number) {
        const r = this.hexagoneRadius;
        const p = this.hexagoneP;
        const x = p + posr * p * 2 + (posq % 2) * p;
        const y = r + posq * r * 1.5;
        return [x, y];
    }

    // рисует шестиугольник из центра
    public drawHexagon(config: {
        posq: number;
        posr: number;
        color?: string;
        text?: string;
        strokeColor?: string;
        radiusMul?: number;
    }) {
        const { posq, posr, color, text, strokeColor, radiusMul = 1 } = config;
        const ctx = this.ctx;
        const r = this.hexagoneRadius * radiusMul;
        const p = this.hexagoneP * radiusMul;

        const [x, y] = this.getCanvasCoords(posr, posq);

        ctx.moveTo(x, y + r); // центральные коорды
        ctx.beginPath();
        ctx.lineTo(x + p, y + r / 2);
        ctx.lineTo(x + p, y - r / 2);
        ctx.lineTo(x, y - r);
        ctx.lineTo(x - p, y - r / 2);
        ctx.lineTo(x - p, y + r / 2);
        ctx.lineTo(x, y + r);
        ctx.closePath();
        if (color) {
            ctx.fillStyle = color;
            ctx.fill();
        }

        if (text) {
            ctx.moveTo(x, y);
            ctx.fillStyle = color ? Colorist.invertHex(color) : "#000";
            ctx.font = `${r*0.8}px Arial`;
            ctx.textAlign = "center";
            ctx.fillText(text, x, y + r / 4);
        }

        // этот костыль придуман для того, чтобы обводка
        // не вылезала за границу шестиугольника
        if (strokeColor) {
            const k = r / 20;
            ctx.moveTo(x, y + r - k); // центральные коорды
            ctx.beginPath();
            ctx.lineTo(x + p - k, y + r / 2);
            ctx.lineTo(x + p - k, y - r / 2);
            ctx.lineTo(x, y - r + k);
            ctx.lineTo(x - p + k, y - r / 2);
            ctx.lineTo(x - p + k, y + r / 2);
            ctx.lineTo(x, y + r - k);
            ctx.closePath();
            ctx.strokeStyle = strokeColor;
            ctx.lineWidth = k * 2;
            ctx.stroke();
        }
    }

    // рисует гекс из центра
    public drawGex(q: number, r: number, gex: IGex) {
        let color = "";
        let strokeColor = "";
        switch (gex.type) {
            case 1: // муравейник
                color = "#FFD700";
                break;
            case 2: // пустой
                color = "#ffffff";
                strokeColor = "#000000";
                break;
            case 3: // грязь
                color = "#79553D";
                break;
            case 4: // кислота
                color = "#00FF00";
                break;
            case 5: // камень
                color = "#909090";
                break;
        }
        this.drawHexagon({
            posq: q,
            posr: r,
            color,
            text: String(gex.cost),
            strokeColor,
        });
    }

    // рисует еду
    public drawFood(q: number, r: number, food: IFood) {
        if (food.amount === 0) return;
        let color = "";
        switch (food.type) {
            case 1: // яблоко
                color = "#FF0000";
                break;
            case 2: // хлеб
                color = "#f5deb3";
                break;
            case 3: // нектар
                color = "#ffa500";
                break;
        }
        this.drawHexagon({
            posq: q,
            posr: r,
            color,
            text: String(food.amount),
            radiusMul: 0.6,
        });
    }

    // рисует муравья
    public drawAnt(
        q: number,
        r: number,
        ant: IAnt | IEnemyAnt,
        isEnemy: boolean = false
    ) {
        let color = "";
        switch (ant.type) {
            case 2: // разведчик
                color = "#00bfff";
                break;
            case 1: // боец
                color = "#bf370f";
                break;
            case 0: // рабочий
                color = "#ffff00";
                break;
        }
        this.drawHexagon({
            posq: q,
            posr: r,
            color,
            text: String(ant.health),
            strokeColor: isEnemy ? "#ff2400" : "#03c03c",
        });
        this.drawFood(q, r, ant.food);
    }

    public drawHome(home: IArena["home"]) {
        for (let piece of home) {
            this.drawHexagon({
                posq: piece.q,
                posr: piece.r,
                color: "#03c03c",
            });
        }
    }
}
