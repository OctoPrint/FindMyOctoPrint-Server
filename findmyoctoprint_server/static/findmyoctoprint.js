(function (global, factory) {
    if (typeof define === "function" && define.amd) {
        define("findmyoctoprint", ["jquery"], factory);
    } else {
        global.findmyoctoprint = factory(window.$);
    }
})(window || this, function($) {

    var options = {
        queryUrl: "./registry",
        urlCheckTimeout: 1000
    };

    var ping = function(url, timeout) {
        var deferred = $.Deferred();

        var img = new Image();
        img.onload = function() {
            deferred.resolve("loaded");
        };
        img.onerror = function() {
            deferred.reject("error");
        };
        img.src = url + "?_=" + Date.now();

        setTimeout(function() {
            if (!deferred.state() != "pending") {
                deferred.reject("timeout");
            }
        }, timeout);

        return deferred.promise();
    };

    var performDiscovery = function() {
        console.log("Scanning...");

        var foundUuids = {};

        var deferred = $.Deferred();

        $.get(options.queryUrl)
            .done(function(response) {
                var promises = [];

                console.log("Got data from", options.queryUrl);

                $.each(response.candidates, function (uuid, candidate) {
                    var promise = new $.Deferred();
                    promises.push(promise);

                    var potentialUrls = [];

                    var checkNextUrl = function () {
                        if (foundUuids[candidate.uuid] != undefined) {
                            promise.resolve();
                            return;
                        }

                        if (potentialUrls.length == 0) {
                            promise.fail();
                            return;
                        }

                        var url = potentialUrls.shift();
                        ping(url.query + ".gif", options.urlCheckTimeout)
                            .done(function () {
                                console.log("candidate", url.target, "checked out");
                                if (foundUuids[candidate.uuid] != undefined) return;
                                var entry = {
                                    url: url.target,
                                    name: url.name,
                                    color: url.color,
                                    uuid: uuid
                                };
                                foundUuids[uuid] = entry;
                                deferred.notify(entry);
                                promise.resolve();
                            })
                            .fail(function () {
                                console.log("candidate", url.target, "didn't check out");
                                checkNextUrl();
                            });
                    };

                    $.each(candidate.urls, function (index, url) {
                        potentialUrls.push({
                            target: url,
                            query: url + candidate.query,
                            name: candidate.name || url,
                            color: candidate.color
                        });
                    });

                    console.log("Checking", potentialUrls.length, "urls for candidate", candidate.uuid);
                    checkNextUrl();
                });

                $.when.apply($, promises).then(function() {
                    deferred.resolve(foundUuids);
                });
            })
            .fail(function() {
                deferred.reject();
            });

        return deferred.promise();
    };

    return {
        options: options,
        discover: performDiscovery
    }
});
