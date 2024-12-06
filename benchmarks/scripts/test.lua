wrk.method = "POST"
wrk.headers["Content-Type"] = "application/json"
wrk.headers["Authorization"] = "Bearer " .. os.getenv("VALID_TOKEN")
wrk.body = [[{
    "prompt": "a magical cosmic unicorn",
    "img_size": 512,
    "guidance_scale": 0,
    "num_inference_steps": 4
}]]

responses = {}
function response(status, headers, body)
    if responses[status] == nil then
        responses[status] = 1
    else
        responses[status] = responses[status] + 1
    end
end

function done(summary, latency, requests)
    io.write("\nResponse Codes:\n")
    for status, count in pairs(responses) do
        io.write(string.format("  [%d] %d responses\n", status, count))
    end
    io.write(string.format("\nFailed Requests: %d\n", summary.errors.status))
end 