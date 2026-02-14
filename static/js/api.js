const API = {
    async get(url) {
        const res = await fetch(url);
        return res.json();
    },
};
