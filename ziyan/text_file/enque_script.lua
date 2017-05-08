-- Creator: Marshall Fate
-- Date: 2016/11/26
-- Time: 16:56

--this lua script is used for redis enque action with two conditions:
--1. fields is diffrent with former fields which refers to old_fields in key threshold of redis
--2. the difference between timestamp and old timestamp(in the key threshold of redis)
--   is longer than the time range (user specified), as a heart beat.
--The data can be enque at least one of above condition met, or just drop it.^_^

--  keys[1]  eqpt_no
--  args[1]  timestamp
--  args[2]  tags
--  args[3]  fields
--  args[4]  measurement
--set parameters:
--how much seconds you want your time range is ???
local time_range = 10
local tags = KEYS[1]
local timestamp = ARGV[1]
local fields = ARGV[2]
local measurement = ARGV[3]
local unit = ARGV[4]


-- FUNCTION PART----------------------------------------------------------------------
local function threshold(fields, timestamp, time_range)
    --    parameters:
    --      fields      table influx json fields.
    --      timestamp   string timestamp
    --      return f_flag,t_flag  boolean
    --    f_flag get True when fields is diffrent with old fields.
    --    t_flag get True when time is longer than threshold time range.

    local old_fields = redis.call("HGET", "threshold", "fields")
    local old_timestamp = redis.call("HGET", "threshold", "timestamp")

    if old_fields == false or old_timestamp == false then
        redis.call('HSET', 'threshold', 'fields', fields)
        redis.call('HSET', 'threshold', 'timestamp', timestamp)
        return true, true
    end

    local f_flag = false
    local t_flag = false
    if fields ~= old_fields then
        f_flag = true
        redis.call("HSET", 'threshold', "fields", fields)
        redis.call("HSET", 'threshold', "timestamp", timestamp)
    end
    if tonumber(timestamp) - tonumber(old_timestamp) > time_range then
        t_flag = true
        redis.call("HSET", 'threshold', "fields", fields)
        redis.call("HSET", 'threshold', "timestamp", timestamp)
    end
    return f_flag, t_flag
end


-- FUNCTION PART----------------------------------------------------------------------



--for using two user variables f_flag and t_flag.
local f_flag = nil; local t_flag = nil

-- use unit to determine time_range.
if cmsgpack.unpack(unit) == 'u' then
    time_range = time_range * 1000000
end


f_flag, t_flag = threshold(fields, cmsgpack.unpack(timestamp), time_range)


if f_flag == true then

    local data = {
        measurement = measurement,
        time = timestamp,
        fields = fields,
        tags = tags,
        unit = unit
    }

    local msg = cmsgpack.pack(data)
    redis.call("RPUSH", "data_queue", msg) -- msg queue
    return 'field enque worked~'

elseif t_flag == true then



    local data = {
        heartbeat = true,
        measurement = measurement,
        time = timestamp,
        fields = fields,
        tags = tags,
        unit = unit
    }
    local msg = cmsgpack.pack(data)
    redis.call("RPUSH", "data_queue", msg) -- msg queue
    return 'heart beat enque worked~'
else
    return 'ignoring schema worked!'
end
