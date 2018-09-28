export interface ITeam {
    logo: string;
    name: string;
    index: number;
    division: string
}

export interface IUser {
    email: string;
    fullname: string;
    role: string;
    password: string;
}

export interface IGame {
    date: string;
    homeTeam: string;
    homeLogo: string;
    awayTeam: string;
    awayLogo: string;
}