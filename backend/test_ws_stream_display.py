#!/usr/bin/env python3
"""
WebSocket Stream Display Test
测试 ws://127.0.0.1:8000/api/sensor/stream 数据展示
"""
import asyncio
import json
from datetime import datetime
import websockets
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout

console = Console()

class SensorStreamDisplay:
    def __init__(self):
        self.latest_data = {}
        self.message_count = 0
        self.start_time = datetime.now()
        
    def create_display(self) -> Layout:
        """创建显示布局"""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="data", size=20),
            Layout(name="footer", size=3)
        )
        
        # Header
        elapsed = (datetime.now() - self.start_time).total_seconds()
        layout["header"].update(
            Panel(
                f"[bold cyan]传感器数据流监控[/bold cyan] | "
                f"消息数: {self.message_count} | "
                f"运行时间: {elapsed:.1f}s",
                style="bold white on blue"
            )
        )
        
        # Data table
        if self.latest_data:
            table = Table(title="最新传感器数据", show_header=True, header_style="bold magenta")
            table.add_column("字段", style="cyan", width=20)
            table.add_column("值", style="green", width=40)
            
            # 基本信息
            table.add_row("传感器ID", str(self.latest_data.get('sensor_id', 'N/A')))
            table.add_row("时间戳", str(self.latest_data.get('timestamp', 'N/A')))
            
            # 加速度数据
            if 'acceleration' in self.latest_data:
                acc = self.latest_data['acceleration']
                table.add_row("加速度 X", f"{acc.get('x', 0):.4f} m/s²")
                table.add_row("加速度 Y", f"{acc.get('y', 0):.4f} m/s²")
                table.add_row("加速度 Z", f"{acc.get('z', 0):.4f} m/s²")
            
            # 角速度数据
            if 'angular_velocity' in self.latest_data:
                gyro = self.latest_data['angular_velocity']
                table.add_row("角速度 X", f"{gyro.get('x', 0):.4f} rad/s")
                table.add_row("角速度 Y", f"{gyro.get('y', 0):.4f} rad/s")
                table.add_row("角速度 Z", f"{gyro.get('z', 0):.4f} rad/s")
            
            # 角度数据
            if 'angle' in self.latest_data:
                angle = self.latest_data['angle']
                table.add_row("角度 Roll", f"{angle.get('roll', 0):.2f}°")
                table.add_row("角度 Pitch", f"{angle.get('pitch', 0):.2f}°")
                table.add_row("角度 Yaw", f"{angle.get('yaw', 0):.2f}°")
            
            # 磁场数据
            if 'magnetic' in self.latest_data:
                mag = self.latest_data['magnetic']
                table.add_row("磁场 X", f"{mag.get('x', 0):.2f}")
                table.add_row("磁场 Y", f"{mag.get('y', 0):.2f}")
                table.add_row("磁场 Z", f"{mag.get('z', 0):.2f}")
            
            layout["data"].update(table)
        else:
            layout["data"].update(Panel("[yellow]等待数据...[/yellow]"))
        
        # Footer
        layout["footer"].update(
            Panel(
                "[dim]按 Ctrl+C 退出[/dim]",
                style="dim"
            )
        )
        
        return layout
    
    async def connect_and_display(self, url: str = "ws://127.0.0.1:8000/api/sensor/stream"):
        """连接 WebSocket 并显示数据"""
        console.print(f"[bold green]正在连接到 {url}...[/bold green]")
        
        try:
            async with websockets.connect(url) as websocket:
                console.print("[bold green]✓ 连接成功！[/bold green]")
                console.print("[dim]开始接收数据...[/dim]\n")
                
                with Live(self.create_display(), refresh_per_second=10, console=console) as live:
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            self.latest_data = data
                            self.message_count += 1
                            live.update(self.create_display())
                        except json.JSONDecodeError as e:
                            console.print(f"[red]JSON 解析错误: {e}[/red]")
                        except Exception as e:
                            console.print(f"[red]处理消息错误: {e}[/red]")
                            
        except websockets.exceptions.WebSocketException as e:
            console.print(f"[bold red]✗ WebSocket 错误: {e}[/bold red]")
        except ConnectionRefusedError:
            console.print("[bold red]✗ 连接被拒绝。请确保后端服务正在运行。[/bold red]")
        except Exception as e:
            console.print(f"[bold red]✗ 错误: {e}[/bold red]")

async def main():
    """主函数"""
    display = SensorStreamDisplay()
    await display.connect_and_display()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]已停止监控[/yellow]")
