import type { IAnt, IEnemyAnt } from "./Entities/Ant";
import type { ICoordinates } from "./Entities/Coordinates";
import type { IFood } from "./Entities/Food";
import type { IGex } from "./Entities/Gex";

export interface IArena {
    ants: IAnt[]; // список ваших муравьёв
    enemies: IEnemyAnt[]; // видимые вражеские муравьи
    food: (IFood & ICoordinates)[]; // ресурсы на карте
    home: ICoordinates[]; // координаты всех трёх гексов муравейника вашей команды
    map: IGex[]; // видимые гексы карты
    nextTurnIn: number; // сколько секунд осталось до следующего хода
    score: number; // текущий счет команды
    spot: ICoordinates; // координаты основного гекса муравейника
    turnNo: number; // номер текущего хода в раунде
}
