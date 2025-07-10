# scripts/performance_test.py
"""
Performance testing script for Knowledge Representation Engine
Tests various endpoints and representation modes
"""

import asyncio
import aiohttp
import time
import json
import statistics
from typing import List, Dict, Any
from datetime import datetime
import sys
from pathlib import Path
from monitor_system import run_monitor
from migrate_database import DatabaseMigrator


class PerformanceTester:
    """Performance testing utility"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []
        
    async def test_endpoint(self, session: aiohttp.ClientSession, method: str, endpoint: str, 
                          data: Dict = None, headers: Dict = None) -> Dict[str, Any]:
        """Test a single endpoint"""
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                async with session.get(f"{self.base_url}{endpoint}", headers=headers) as response:
                    content = await response.text()
                    status_code = response.status
            elif method.upper() == "POST":
                async with session.post(f"{self.base_url}{endpoint}", json=data, headers=headers) as response:
                    content = await response.text()
                    status_code = response.status
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response_time = time.time() - start_time
            
            return {
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "response_time": response_time,
                "success": 200 <= status_code < 400,
                "content_length": len(content),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            return {
                "endpoint": endpoint,
                "method": method,
                "status_code": 0,
                "response_time": response_time,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def load_test(self, endpoint: str, method: str = "GET", data: Dict = None, 
                       concurrent_users: int = 10, requests_per_user: int = 100) -> Dict[str, Any]:
        """Run load test on an endpoint"""
        print(f"🔄 Load testing {method} {endpoint} with {concurrent_users} users, {requests_per_user} requests each")
        
        async def user_session(user_id: int):
            """Simulate a user session"""
            user_results = []
            
            async with aiohttp.ClientSession() as session:
                for i in range(requests_per_user):
                    result = await self.test_endpoint(session, method, endpoint, data)
                    result["user_id"] = user_id
                    result["request_number"] = i + 1
                    user_results.append(result)
                    
                    # Small delay between requests
                    await asyncio.sleep(0.1)
            
            return user_results
        
        # Start all user sessions concurrently
        start_time = time.time()
        tasks = [user_session(i) for i in range(concurrent_users)]
        all_results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Flatten results
        flat_results = [result for user_results in all_results for result in user_results]
        
        # Calculate statistics
        response_times = [r["response_time"] for r in flat_results if r["success"]]
        success_count = sum(1 for r in flat_results if r["success"])
        total_requests = len(flat_results)
        
        stats = {
            "endpoint": endpoint,
            "method": method,
            "total_requests": total_requests,
            "successful_requests": success_count,
            "failed_requests": total_requests - success_count,
            "success_rate": success_count / total_requests if total_requests > 0 else 0,
            "total_time": total_time,
            "requests_per_second": total_requests / total_time,
            "concurrent_users": concurrent_users,
            "response_times": {
                "min": min(response_times) if response_times else 0,
                "max": max(response_times) if response_times else 0,
                "mean": statistics.mean(response_times) if response_times else 0,
                "median": statistics.median(response_times) if response_times else 0,
                "p95": statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else 0,
                "p99": statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else 0
            }
        }
        
        return stats
    
    async def test_representation_modes(self) -> Dict[str, Any]:
        """Test all representation modes"""
        print("🎨 Testing representation modes performance...")
        
        representation_modes = [
            "plain_text", "color_coded", "knowledge_graph", "analogical",
            "persona_eli5", "persona_expert", "timeline", "summary", "detailed"
        ]
        
        test_query = {
            "query": "Explain artificial intelligence and machine learning",
            "context": {"user_level": "intermediate"},
            "user_preferences": {"complexity_level": "medium"}
        }
        
        mode_results = []
        
        async with aiohttp.ClientSession() as session:
            for mode in representation_modes:
                test_data = {**test_query, "representation_mode": mode}
                
                # Test each mode multiple times
                mode_times = []
                for _ in range(5):
                    result = await self.test_endpoint(session, "POST", "/api/process", test_data)
                    if result["success"]:
                        mode_times.append(result["response_time"])
                
                mode_results.append({
                    "mode": mode,
                    "response_times": mode_times,
                    "avg_response_time": statistics.mean(mode_times) if mode_times else 0,
                    "success_rate": len(mode_times) / 5
                })
        
        return {
            "representation_modes": mode_results,
            "fastest_mode": min(mode_results, key=lambda x: x["avg_response_time"])["mode"],
            "slowest_mode": max(mode_results, key=lambda x: x["avg_response_time"])["mode"]
        }
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive performance test suite"""
        print("🚀 Starting comprehensive performance test suite...")
        
        results = {
            "test_start_time": datetime.now().isoformat(),
            "tests": {}
        }
        
        # Test health endpoint
        results["tests"]["health_check"] = await self.load_test("/health", "GET", concurrent_users=5, requests_per_user=20)
        
        # Test API documentation
        results["tests"]["api_docs"] = await self.load_test("/docs", "GET", concurrent_users=3, requests_per_user=10)
        
        # Test main page
        results["tests"]["main_page"] = await self.load_test("/", "GET", concurrent_users=5, requests_per_user=10)
        
        # Test admin panel
        results["tests"]["admin_panel"] = await self.load_test("/admin", "GET", concurrent_users=2, requests_per_user=5)
        
        # Test representation modes
        results["tests"]["representation_modes"] = await self.test_representation_modes()
        
        # Test file upload
        results["tests"]["file_upload"] = await self.load_test("/api/upload", "POST", 
                                                             data={"test": "data"}, 
                                                             concurrent_users=3, requests_per_user=5)
        
        results["test_end_time"] = datetime.now().isoformat()
        
        return results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate performance test report"""
        report = []
        report.append("📊 Performance Test Report")
        report.append("=" * 50)
        report.append(f"Test Period: {results['test_start_time']} to {results['test_end_time']}")
        report.append("")
        
        for test_name, test_results in results["tests"].items():
            report.append(f"🔍 {test_name.replace('_', ' ').title()}")
            report.append("-" * 30)
            
            if test_name == "representation_modes":
                report.append(f"Fastest Mode: {test_results['fastest_mode']}")
                report.append(f"Slowest Mode: {test_results['slowest_mode']}")
                report.append("")
                
                for mode_result in test_results["representation_modes"]:
                    report.append(f"  {mode_result['mode']}: {mode_result['avg_response_time']:.3f}s avg")
            else:
                report.append(f"Total Requests: {test_results['total_requests']}")
                report.append(f"Success Rate: {test_results['success_rate']:.1%}")
                report.append(f"Requests/Second: {test_results['requests_per_second']:.2f}")
                report.append(f"Response Time - Mean: {test_results['response_times']['mean']:.3f}s")
                report.append(f"Response Time - P95: {test_results['response_times']['p95']:.3f}s")
            
            report.append("")
        
        return "\n".join(report)

async def run_performance_tests():
    """Run performance tests"""
    tester = PerformanceTester()
    results = await tester.run_comprehensive_test()
    
    # Generate and save report
    report = tester.generate_report(results)
    
    # Save detailed results
    with open(f"performance_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    # Save report
    with open(f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", 'w') as f:
        f.write(report)
    
    print(report)
    print("\n✅ Performance tests completed!")

if __name__ == "__main__":
    # Run database migration
    if len(sys.argv) > 1 and sys.argv[1] == "migrate":
        migrator = DatabaseMigrator()
        migrator.run_migrations()
    
    # Run monitoring
    elif len(sys.argv) > 1 and sys.argv[1] == "monitor":
        run_monitor()
    
    # Run performance tests
    elif len(sys.argv) > 1 and sys.argv[1] == "perf":
        asyncio.run(run_performance_tests())
    
    else:
        print("Usage:")
        print("  python scripts/migrate_database.py migrate")
        print("  python scripts/monitor_system.py monitor")
        print("  python scripts/performance_test.py perf")
