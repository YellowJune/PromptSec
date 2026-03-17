import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface HeatmapProps {
  heatmapData: number[][];
  tokens: string[];
  layers: string[];
}

export default function Heatmap({ heatmapData, tokens, layers }: HeatmapProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!svgRef.current || !heatmapData.length || !tokens.length || !layers.length) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const margin = { top: 60, right: 30, bottom: 80, left: 100 };
    const cellSize = Math.min(40, Math.max(20, 600 / tokens.length));
    const width = tokens.length * cellSize;
    const height = layers.length * cellSize;

    svg.attr('width', width + margin.left + margin.right)
       .attr('height', height + margin.top + margin.bottom);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const x = d3.scaleBand<string>()
      .range([0, width])
      .domain(tokens)
      .padding(0.05);

    const y = d3.scaleBand<string>()
      .range([0, height])
      .domain(layers)
      .padding(0.05);

    const flatData = heatmapData.flat();
    const minVal = d3.min(flatData) ?? 0;
    const maxVal = d3.max(flatData) ?? 1;

    const colorScale = d3.scaleSequential()
      .interpolator(d3.interpolateViridis)
      .domain([minVal, maxVal]);

    // Build rectangles
    const cellData: { row: number; col: number; value: number }[] = [];
    heatmapData.forEach((row, i) => {
      row.forEach((value, j) => {
        cellData.push({ row: i, col: j, value });
      });
    });

    const tooltip = d3.select(tooltipRef.current);

    g.selectAll('rect')
      .data(cellData)
      .enter()
      .append('rect')
      .attr('x', d => x(tokens[d.col]) ?? 0)
      .attr('y', d => y(layers[d.row]) ?? 0)
      .attr('width', x.bandwidth())
      .attr('height', y.bandwidth())
      .attr('rx', 2)
      .style('fill', d => colorScale(d.value))
      .style('stroke', 'hsl(222.2, 84%, 4.9%)')
      .style('stroke-width', 1)
      .style('cursor', 'pointer')
      .on('mouseover', function () {
        d3.select(this).style('stroke', '#60a5fa').style('stroke-width', 2);
        tooltip.style('opacity', 1);
      })
      .on('mousemove', function (event, d) {
        tooltip
          .html(`<strong>Token:</strong> ${tokens[d.col]}<br/><strong>Layer:</strong> ${layers[d.row]}<br/><strong>Influence:</strong> ${d.value.toFixed(4)}`)
          .style('left', `${event.pageX + 12}px`)
          .style('top', `${event.pageY - 28}px`);
      })
      .on('mouseleave', function () {
        d3.select(this).style('stroke', 'hsl(222.2, 84%, 4.9%)').style('stroke-width', 1);
        tooltip.style('opacity', 0);
      });

    // X axis
    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x))
      .selectAll('text')
      .style('fill', 'hsl(210, 40%, 85%)')
      .style('font-size', '11px')
      .attr('transform', 'rotate(-45)')
      .style('text-anchor', 'end');

    // Y axis
    g.append('g')
      .call(d3.axisLeft(y))
      .selectAll('text')
      .style('fill', 'hsl(210, 40%, 85%)')
      .style('font-size', '11px');

    // Style axes
    g.selectAll('.domain').style('stroke', 'hsl(217.2, 32.6%, 25%)');
    g.selectAll('.tick line').style('stroke', 'hsl(217.2, 32.6%, 25%)');

    // Title
    svg.append('text')
      .attr('x', (width + margin.left + margin.right) / 2)
      .attr('y', 30)
      .attr('text-anchor', 'middle')
      .style('fill', 'hsl(210, 40%, 98%)')
      .style('font-size', '16px')
      .style('font-weight', '600')
      .text('Token Influence Heatmap (\u0394H)');

    // Color legend
    const legendWidth = 200;
    const legendHeight = 12;
    const legendX = width + margin.left - legendWidth;
    const legendY = margin.top - 35;

    const defs = svg.append('defs');
    const linearGradient = defs.append('linearGradient').attr('id', 'heatmap-gradient');
    const nStops = 10;
    for (let i = 0; i <= nStops; i++) {
      const t = i / nStops;
      linearGradient.append('stop')
        .attr('offset', `${t * 100}%`)
        .attr('stop-color', colorScale(minVal + t * (maxVal - minVal)));
    }

    svg.append('rect')
      .attr('x', legendX)
      .attr('y', legendY)
      .attr('width', legendWidth)
      .attr('height', legendHeight)
      .attr('rx', 3)
      .style('fill', 'url(#heatmap-gradient)');

    svg.append('text')
      .attr('x', legendX)
      .attr('y', legendY + legendHeight + 12)
      .style('fill', 'hsl(215, 20.2%, 65.1%)')
      .style('font-size', '10px')
      .text(minVal.toFixed(2));

    svg.append('text')
      .attr('x', legendX + legendWidth)
      .attr('y', legendY + legendHeight + 12)
      .attr('text-anchor', 'end')
      .style('fill', 'hsl(215, 20.2%, 65.1%)')
      .style('font-size', '10px')
      .text(maxVal.toFixed(2));

  }, [heatmapData, tokens, layers]);

  return (
    <div className="relative overflow-x-auto">
      <svg ref={svgRef} />
      <div ref={tooltipRef} className="d3-tooltip" style={{ opacity: 0 }} />
    </div>
  );
}
