import type { ICoordinates } from "./Coordinates";
import type { IFood } from "./Food";

export interface IEnemyAnt extends ICoordinates {
    type: number; // тип муравья
    health: number;  // текущее количество жизней
    food: IFood; // ресурс, который несёт муравей
    attack: number; // ?
}

export interface IAnt extends ICoordinates{
    id: string; // уникальный идентификатор муравья
    type: number; // тип муравья
    health: number; // текущее количество жизней
    food: IFood; // ресурс, который несёт муравей
    lastMove?: ICoordinates[]; // маршрут, по которому юнит передвигался в предыдущий ход
    move?: ICoordinates[]; // маршрут, заданный на текущий ход
    lastAttack?: ICoordinates; // координаты, по которым была совершена последняя атака
    lastEnemyAnt?: string; // ID вражеского муравья, по которому нанесён урон
}