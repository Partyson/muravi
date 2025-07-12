import axios from "axios";
import type { IArena } from "./DTO";
import { arenaExample } from "./arenaExample";

// класс, работающий с запросами
export class Requester {
    private URL: string;
    private TOKEN: string;
    constructor(url: string, token: string) {
        this.URL=url
        this.TOKEN=token
    }

    public async requestArena() {
        //TODO: удалить эту строку, когда откроется сервер
        return arenaExample as IArena;
        
        const path = this.URL + '/api/arena'
        const {data} = await axios.get<IArena>(path, {
            headers: {
                'X-Auth-Token': this.TOKEN
            }
        })

        return data;
    }

}