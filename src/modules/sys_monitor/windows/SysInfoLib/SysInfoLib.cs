using System.Management;
using System.Diagnostics;

namespace SysInfoLib
{
    public class SystemInfoModel
    {
        public string CpuName { get; set; }
        public int CpuCores { get; set; }
        public double CpuUsage { get; set; }
        public long TotalMemoryMB { get; set; }
        public long AvailableMemoryMB { get; set; }
    }

    public class SystemInfoProvider
    {
        public static SystemInfoModel GetSystemInfo()
        {
            var info = new SystemInfoModel();

            // Get CPU info
            using (var searcher = new ManagementObjectSearcher("SELECT * FROM Win32_Processor"))
            {
                foreach (ManagementObject obj in searcher.Get())
                {
                    info.CpuName = obj["Name"]?.ToString();
                    info.CpuCores = Convert.ToInt32(obj["NumberOfCores"]);
                }
            }

            // Get memory info
            using (var searcher = new ManagementObjectSearcher("SELECT * FROM Win32_ComputerSystem"))
            {
                foreach (ManagementObject obj in searcher.Get())
                {
                    info.TotalMemoryMB = Convert.ToInt64(obj["TotalPhysicalMemory"]) / (1024 * 1024);
                }
            }

            // Get CPU usage (basic)
            var cpuCounter = new PerformanceCounter("Processor", "% Processor Time", "_Total");
            cpuCounter.NextValue(); // First call returns 0
            System.Threading.Thread.Sleep(100);
            info.CpuUsage = Math.Round(cpuCounter.NextValue(), 2);

            return info;
        }
    }
}