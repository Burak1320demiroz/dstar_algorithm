import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from typing import List, Tuple, Optional
import matplotlib.animation as animation

class PathPlotter:
    """Yol planlama görselleştirme sınıfı"""
    
    def __init__(self, figsize=(12, 10)):
        self.figsize = figsize
        self.fig = None
        self.ax = None
        
    def setup_plot(self, grid_map, title="D* Lite Path Planning"):
        """Plot'u ayarla"""
        self.fig, self.ax = plt.subplots(figsize=self.figsize)
        self.ax.set_xlim(-0.5, grid_map.width - 0.5)
        self.ax.set_ylim(-0.5, grid_map.height - 0.5)
        self.ax.set_aspect('equal')
        self.ax.set_title(title, fontsize=16)
        self.ax.set_xlabel('X', fontsize=12)
        self.ax.set_ylabel('Y', fontsize=12)
        
        # Grid çizgileri
        self.ax.set_xticks(range(0, grid_map.width, max(1, grid_map.width//20)))
        self.ax.set_yticks(range(0, grid_map.height, max(1, grid_map.height//20)))
        self.ax.grid(True, alpha=0.3)
    
    def plot_grid(self, grid_map):
        """Grid haritasını çiz"""
        # Renk haritası
        colors = np.zeros((grid_map.height, grid_map.width, 3))
        
        for y in range(grid_map.height):
            for x in range(grid_map.width):
                if grid_map.grid[y, x] == grid_map.OBSTACLE:
                    colors[y, x] = [0, 0, 0]  # Siyah - engel
                elif grid_map.grid[y, x] == grid_map.ROUGH_TERRAIN:
                    colors[y, x] = [0.7, 0.4, 0.1]  # Kahverengi - zor arazi
                else:
                    colors[y, x] = [1, 1, 1]  # Beyaz - serbest alan
        
        self.ax.imshow(colors, origin='lower', extent=[-0.5, grid_map.width-0.5, 
                                                      -0.5, grid_map.height-0.5])
    
    def plot_path(self, grid_map, path: List[Tuple[int, int]], 
                 start: Tuple[int, int], goal: Tuple[int, int], 
                 title="D* Lite Path Planning"):
        """Yolu görselleştir"""
        self.setup_plot(grid_map, title)
        self.plot_grid(grid_map)
        
        # Yol çizimi
        if path:
            path_x = [p[0] for p in path]
            path_y = [p[1] for p in path]
            self.ax.plot(path_x, path_y, 'b-', linewidth=3, label=f'Path (length: {len(path)})')
            self.ax.plot(path_x, path_y, 'bo', markersize=4, alpha=0.6)
        
        # Başlangıç ve hedef noktalar
        self.ax.plot(start[0], start[1], 'go', markersize=15, label='Start', markeredgecolor='black', markeredgewidth=2)
        self.ax.plot(goal[0], goal[1], 'ro', markersize=15, label='Goal', markeredgecolor='black', markeredgewidth=2)
        
        self.ax.legend(fontsize=12)
        return self.fig
    
    def plot_vehicle_trajectory(self, grid_map, path: List[Tuple[int, int]], 
                               vehicle_trajectory: List, title="Vehicle Trajectory"):
        """Araç trajektorisini görselleştir"""
        self.setup_plot(grid_map, title)
        self.plot_grid(grid_map)
        
        # Planlanan yol
        if path:
            path_x = [p[0] for p in path]
            path_y = [p[1] for p in path]
            self.ax.plot(path_x, path_y, 'b--', linewidth=2, alpha=0.7, label='Planned Path')
        
        # Araç trajektorisi
        if vehicle_trajectory:
            traj_x = [state.x for state in vehicle_trajectory]
            traj_y = [state.y for state in vehicle_trajectory]
            self.ax.plot(traj_x, traj_y, 'r-', linewidth=3, label='Vehicle Trajectory')
            
            # Araç yönelimleri (oklar)
            step = max(1, len(vehicle_trajectory) // 20)
            for i in range(0, len(vehicle_trajectory), step):
                state = vehicle_trajectory[i]
                dx = 2 * np.cos(state.theta)
                dy = 2 * np.sin(state.theta)
                self.ax.arrow(state.x, state.y, dx, dy, 
                            head_width=0.8, head_length=0.5, 
                            fc='red', ec='red', alpha=0.7)
        
        self.ax.legend(fontsize=12)
        return self.fig
    
    def animate_vehicle(self, grid_map, path: List[Tuple[int, int]], 
                       vehicle_trajectory: List, save_path: Optional[str] = None):
        """Araç hareketini animasyon olarak göster"""
        self.setup_plot(grid_map, "Vehicle Animation")
        self.plot_grid(grid_map)
        
        # Statik elementler
        if path:
            path_x = [p[0] for p in path]
            path_y = [p[1] for p in path]
            self.ax.plot(path_x, path_y, 'b--', linewidth=2, alpha=0.5, label='Planned Path')
        
        # Animasyon elementleri
        vehicle_dot, = self.ax.plot([], [], 'ro', markersize=10, label='Vehicle')
        trajectory_line, = self.ax.plot([], [], 'r-', linewidth=2, alpha=0.7)
        orientation_arrow = patches.FancyArrowPatch((0, 0), (0, 0), 
                                                   arrowstyle='->', mutation_scale=20, color='red')
        self.ax.add_patch(orientation_arrow)
        
        self.ax.legend()
        
        def animate(frame):
            if frame < len(vehicle_trajectory):
                state = vehicle_trajectory[frame]
                
                # Araç pozisyonu
                vehicle_dot.set_data([state.x], [state.y])
                
                # Geçmiş trajektori
                traj_x = [vehicle_trajectory[i].x for i in range(frame + 1)]
                traj_y = [vehicle_trajectory[i].y for i in range(frame + 1)]
                trajectory_line.set_data(traj_x, traj_y)
                
                # Yönelim oku
                dx = 3 * np.cos(state.theta)
                dy = 3 * np.sin(state.theta)
                orientation_arrow.set_positions((state.x, state.y), 
                                              (state.x + dx, state.y + dy))
            
            return vehicle_dot, trajectory_line, orientation_arrow
        
        anim = animation.FuncAnimation(self.fig, animate, frames=len(vehicle_trajectory),
                                     interval=100, blit=True, repeat=True)
        
        if save_path:
            anim.save(save_path, writer='pillow', fps=10)
        
        return anim
    
    def plot_search_progress(self, grid_map, expanded_nodes: List[Tuple[int, int]], 
                           path: List[Tuple[int, int]], start: Tuple[int, int], 
                           goal: Tuple[int, int]):
        """Arama ilerlemesini göster"""
        self.setup_plot(grid_map, "Search Progress Visualization")
        self.plot_grid(grid_map)
        
        # Genişletilen düğümler
        if expanded_nodes:
            exp_x = [n[0] for n in expanded_nodes]
            exp_y = [n[1] for n in expanded_nodes]
            self.ax.scatter(exp_x, exp_y, c='yellow', s=20, alpha=0.6, 
                          label=f'Expanded Nodes ({len(expanded_nodes)})')
        
        # Bulunan yol
        if path:
            path_x = [p[0] for p in path]
            path_y = [p[1] for p in path]
            self.ax.plot(path_x, path_y, 'b-', linewidth=4, label=f'Found Path ({len(path)})')
        
        # Başlangıç ve hedef
        self.ax.plot(start[0], start[1], 'go', markersize=15, label='Start', 
                    markeredgecolor='black', markeredgewidth=2)
        self.ax.plot(goal[0], goal[1], 'ro', markersize=15, label='Goal', 
                    markeredgecolor='black', markeredgewidth=2)
        
        self.ax.legend()
        return self.fig
    
    def show(self):
        """Plot'u göster"""
        plt.tight_layout()
        plt.show()
    
    def save(self, filename: str, dpi=300):
        """Plot'u kaydet"""
        if self.fig:
            self.fig.savefig(filename, dpi=dpi, bbox_inches='tight')
