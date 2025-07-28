# [official documentation link](https://langchain-ai.github.io/langgraph/how-tos/memory/add-memory/#use-in-production)

```bash
pip install langgraph-checkpoint-redis
```
**Note:** You need to call checkpointer.setup() the first time you're using Redis checkpointer

# error
```json
{
    "error": "Required Redis db module search >= 20600 OR searchlight >= 20600 not installed. See Redis Stack docs at https://redis.io/docs/latest/operate/oss_and_stack/install/install-stack/.",
    "status": "error"
}
```
### to solve this error neee to use [redis stack server contaienr](https://hub.docker.com/r/redis/redis-stack-server
)


# error 
- Can't handle RDB format version 12
- Fatal error loading the DB, check server logs. Exiting.

###  What this means
This error typically happens when:

- You're using a newer version of Redis Stack that cannot read an older RDB file, or

- You're reusing an existing RDB file (dump.rdb) from a non-compatible Redis version.

### Solution
- You need to clear the redis-data volume so Redis starts fresh without the incompatible .rdb file.
#### Run the following in your terminal
```bash
docker-compose down -v  # stops and removes containers and volumes
docker-compose up --build
```

