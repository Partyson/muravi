import { Colorist } from "../Colorist";
import type { IArena } from "../Requester/DTO";
import type { IAnt, IEnemyAnt } from "../Requester/Entities/Ant";
import type { ICoordinates } from "../Requester/Entities/Coordinates";
import type { IFood } from "../Requester/Entities/Food";
import type { IGex } from "../Requester/Entities/Gex";
import { COLORS } from "./Colors";

// класс, который рисует
export class CanvasArtist {
    public canvas: HTMLCanvasElement;
    private ctx: CanvasRenderingContext2D;
    public hexagoneRadius: number;
    public hexagoneP: number;
    public scale: number;
    public translate: [number, number];
    constructor(canvas: HTMLCanvasElement, hexagoneRadius: number = 20) {
        this.canvas = canvas;
        this.ctx = canvas.getContext("2d") as CanvasRenderingContext2D;
        this.hexagoneRadius = hexagoneRadius;
        // длина перпендикуляра из центра к стороне
        this.hexagoneP = hexagoneRadius * (Math.sqrt(3) / 2);
        this.scale = 3;
        this.translate = [0, 0];
    }

    public getCanvasCoords(posr: number, posq: number) {
        const r = this.hexagoneRadius;
        const p = this.hexagoneP;
        const x = p + (posr + 1000) * p * 2 + (posq % 2) * p;
        const y = r + (posq + 1000) * r * 1.5;
        return [x, y];
    }

    public clear() {
        this.ctx.clearRect(0, 0, 10000000, 10000000);
    }

    // рисует шестиугольник из центра
    public drawHexagon(config: {
        posq: number;
        posr: number;
        color?: string;
        text?: string;
        textMul?: number;
        strokeColor?: string;
        radiusMul?: number;
    }) {
        const {
            posq,
            posr,
            color,
            text,
            textMul = 0.8,
            strokeColor,
            radiusMul = 1,
        } = config;
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
            ctx.font = `${r * textMul}px Arial`;
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

    public drawCircle(config: {
        posq: number;
        posr: number;
        color?: string;
        text?: string;
        textMul?: number;
        strokeColor?: string;
        radiusMul?: number;
    }) {
        const {
            posq,
            posr,
            color,
            text,
            textMul = 0.8,
            strokeColor,
            radiusMul = 1,
        } = config;
        const ctx = this.ctx;
        const r = this.hexagoneRadius * radiusMul;
        const p = this.hexagoneP * radiusMul;
        const [x, y] = this.getCanvasCoords(posr, posq);

        // этот костыль придуман для того, чтобы обводка
        // не вылезала за границу шестиугольника
        ctx.moveTo(x, y + r); // центральные коорды
        if (strokeColor) {
            const k = p / 20;
            ctx.arc(x, y, k, 0, 2 * Math.PI);
            ctx.strokeStyle = strokeColor;
            ctx.stroke();
        }

        ctx.beginPath();
        ctx.arc(x, y, p, 0, 2 * Math.PI);
        ctx.closePath();
        if (color) {
            ctx.fillStyle = color;
            ctx.fill();
        }

        if (text) {
            ctx.moveTo(x, y);
            ctx.fillStyle = color ? Colorist.invertHex(color) : "#000";
            ctx.font = `${r * textMul}px Arial`;
            ctx.textAlign = "center";
            ctx.fillText(text, x, y + r / 4);
        }
    }

    // рисует стрелку из гекса в гекс
    public drawArrow(
        q1: number,
        r1: number,
        move: ICoordinates[],
        color: string
    ) {
        let moveCoords: number[][] = [this.getCanvasCoords(r1, q1)];
        for (const step of move) {
            moveCoords.push(this.getCanvasCoords(step.r, step.q));
        }
        // const [x2, y2] = ;
        const arrowSize = this.hexagoneRadius / 2;
        this.ctx.strokeStyle = color;
        this.ctx.fillStyle = color;
        this.ctx.lineWidth = arrowSize / 6;
        // this.ctx.beginPath();
        this.ctx.moveTo(moveCoords[0][0], moveCoords[0][1]);
        for (const stepCoords of moveCoords) {
            this.ctx.lineTo(stepCoords[0], stepCoords[1]);
        }
        this.ctx.stroke();
        // this.ctx.closePath();

        const [x2, y2] = moveCoords[moveCoords.length - 1];
        const [x1, y1] = moveCoords[moveCoords.length - 2];
        const angle = Math.atan2(y2 - y1, x2 - x1);

        this.ctx.moveTo(x2, y2);
        this.ctx.beginPath();
        this.ctx.lineTo(
            x2 - arrowSize * Math.cos(angle - Math.PI / 6),
            y2 - arrowSize * Math.sin(angle - Math.PI / 6)
        );
        this.ctx.lineTo(
            x2 - arrowSize * Math.cos(angle + Math.PI / 6),
            y2 - arrowSize * Math.sin(angle + Math.PI / 6)
        );
        this.ctx.lineTo(x2, y2);
        this.ctx.fill(); // Заливаем стрелку
        this.ctx.closePath();
    }

    // рисует гекс из центра
    public drawGex(q: number, r: number, gex: IGex) {
        let color = "";
        switch (gex.type) {
            case 1: // муравейник
                color = COLORS.anthill_gex;
                break;
            case 2: // пустой
                color = COLORS.empty_gex;
                break;
            case 3: // грязь
                color = COLORS.dirt_gex;
                break;
            case 4: // кислота
                color = COLORS.acid_gex;
                break;
            case 5: // камень
                color = COLORS.stone_gex;
                break;
        }
        this.drawHexagon({
            posq: q,
            posr: r,
            color,
            text: gex.q + " | " + gex.r,
            textMul: 0.35,
        });
    }

    // рисует еду
    public drawFood(q: number, r: number, food: IFood) {
        if (food.amount === 0) return;
        let color = "";
        switch (food.type) {
            case 1: // яблоко
                color = COLORS.apple_food;
                break;
            case 2: // хлеб
                color = COLORS.bread_food;
                break;
            case 3: // нектар
                color = COLORS.nectar_food;
                break;
        }
        this.drawCircle({
            posq: q,
            posr: r,
            color,
            text: String(food.amount),
            radiusMul: 0.5,
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
                color = COLORS.scout_ant;
                break;
            case 1: // боец
                color = COLORS.fighter_ant;
                break;
            case 0: // рабочий
                color = COLORS.worker_ant;
                break;
        }
        this.drawHexagon({
            posq: q,
            posr: r,
            color,
            text: String(ant.health),
            strokeColor: isEnemy ? COLORS.enemy : COLORS.ally,
            radiusMul: 0.7,
        });
        this.drawFood(q, r, ant.food);
    }

    public drawHome(home: IArena["home"]) {
        for (let piece of home) {
            this.drawHexagon({
                posq: piece.q,
                posr: piece.r,
                color: COLORS.home_gex,
            });
        }
    }

    private applyTransform() {
        this.ctx.setTransform(1, 0, 0, 1, 0, 0);
        this.ctx.setTransform(
            this.scale,
            0,
            0,
            this.scale,
            this.translate[0] * this.scale,
            this.translate[1] * this.scale
        );
    }

    public zoom(scale: number) {
        const newScale = this.scale + scale;
        if (newScale <= 0) {
            this.scale = 1;
        } else if (newScale >= 4) {
            this.scale = 4;
        } else {
            this.scale = newScale;
        }
        this.applyTransform();
    }

    public move(x: number, y: number) {
        // this.ctx.resetTransform();
        this.translate = [this.translate[0] + x, this.translate[1] + y];
        this.applyTransform();
    }

    public goTo(x: number, y: number) {
        this.translate = [x, y];
        this.applyTransform();
    }
}
