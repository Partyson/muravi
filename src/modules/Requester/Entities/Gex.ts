import type { ICoordinates } from "./Coordinates";

export interface IGex extends ICoordinates{
    type: number; // тип гекса
    cost: number; // стоимость перемещения на гекс
}