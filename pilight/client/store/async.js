import fetch from 'isomorphic-fetch';

export const Status = {
    INVALID: 'INVALID',
    FETCHING: 'FETCHING',
    VALID: 'VALID',
};

// Kind of hacky... But this is set externally from root.js on bootstrap.
let csrfToken = null;
export function setCsrfToken(token) {
    csrfToken = token;
}

export const fetchObjectPromise = (uri, callback, errorCallback) => {
    return fetch(uri, {credentials: 'same-origin', headers: {Accept: 'application/json'}})
        .then((response) => {
            if (response.status >= 400) {
                errorCallback(`Bad response from server: ${response.status}`);
            }
            return response.json();
        })
        .then((data) => {
            if (!data.success) {
                errorCallback(data.error);
            } else {
                callback(data);
            }
            return data;
        });
};

export const postObjectPromise = (uri, value, callback, errorCallback) => {
    let opts = {
        method: 'POST',
        credentials: 'same-origin',
        body: JSON.stringify(value),
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
    };

    return fetch(uri, opts)
        .then((response) => {
            if (response.status >= 400) {
                errorCallback(`Bad response from server: ${response.status}`);
            }
            return response.json();
        })
        .then((data) => {
            if (!data.success) {
                console.log(data);
                errorCallback(data.error);
            } else {
                callback(data);
            }
            return data;
        });
};
