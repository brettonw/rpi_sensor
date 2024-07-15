#! /usr/bin/env python3

# docker stats --no-stream --format "{{ json . }}"
# {"BlockIO":"16.4MB / 135kB","CPUPerc":"0.01%","Container":"eb2c2aea8b68","ID":"eb2c2aea8b68","MemPerc":"15.00%","MemUsage":"76.82MiB / 512MiB","Name":"inf1","NetIO":"104kB / 1.3MB","PIDs":"2"}
# {"BlockIO":"16.6MB / 73.7kB","CPUPerc":"0.01%","Container":"484d4f8e84a1","ID":"484d4f8e84a1","MemPerc":"15.18%","MemUsage":"77.74MiB / 512MiB","Name":"inf2","NetIO":"121kB / 148kB","PIDs":"2"}

# docker stats --no-stream --format "{\"name\": \"{{ .Name }}\", \"memory_usage\": \"{{ .MemUsage }}\", \"memory_percent\": \"{{ .MemPerc }}\", \"cpu_percent\": \"{{ .CPUPerc }}\"},"
# {"name": "inf1", "memory_usage": "76.82MiB / 512MiB", "memory_percent": "15.00%", "cpu_percent": "0.01%"},
# {"name": "inf2", "memory_usage": "77.74MiB / 512MiB", "memory_percent": "15.18%", "cpu_percent": "0.00%"},
