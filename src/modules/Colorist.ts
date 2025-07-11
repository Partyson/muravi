// класс, работающий со цветом
export class Colorist {
    public static invertHex(hex: string) {
        return (
            "#" +
            //@ts-ignore
            hex
                .match(/[a-f0-9]{2}/gi)
                .map((e) =>
                    ((255 - parseInt(e, 16)) | 0)
                        .toString(16)
                        .replace(/^([a-f0-9])$/, "0$1")
                )
                .join("")
        );
    }
}
