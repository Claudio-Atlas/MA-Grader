"""
test_scatterplot.py — Unit tests for check_scatterplot module

Tests the scatterplot grading logic including:
- Chart presence detection
- Title and axis label checks
- Trendline detection
- Trendline extension validation
"""

import pytest
from unittest.mock import MagicMock, PropertyMock
from openpyxl.chart import ScatterChart
from openpyxl.chart.series import XYSeries


class TestCheckScatterplotImport:
    """Test that the module can be imported."""
    
    def test_import_check_scatterplot(self):
        """Should import check_scatterplot function."""
        from graders.income_analysis.check_scatterplot import check_scatterplot
        assert callable(check_scatterplot)


class TestCheckScatterplotNoChart:
    """Tests when no chart is present."""
    
    def test_no_charts_on_worksheet(self):
        """Should return 0 score when worksheet has no charts."""
        from graders.income_analysis.check_scatterplot import check_scatterplot
        
        # Create mock worksheet with no charts
        ws = MagicMock()
        ws._charts = []
        
        chart_score, trendline_score, feedback = check_scatterplot(ws)
        
        assert chart_score == 0.0 and trendline_score == 0.0
        assert any(code == "IA_SCATTER_NOT_FOUND" for code, _ in feedback)
    
    def test_only_non_scatter_charts(self):
        """Should return 0 when only non-scatter charts exist."""
        from graders.income_analysis.check_scatterplot import check_scatterplot
        
        # Create mock worksheet with a non-scatter chart
        ws = MagicMock()
        non_scatter_chart = MagicMock()  # Not a ScatterChart instance
        ws._charts = [non_scatter_chart]
        
        chart_score, trendline_score, feedback = check_scatterplot(ws)
        
        assert chart_score == 0.0 and trendline_score == 0.0
        assert any(code == "IA_SCATTER_NOT_FOUND" for code, _ in feedback)


class TestCheckScatterplotChartPresent:
    """Tests for chart presence (3 points)."""
    
    @pytest.fixture
    def mock_scatter_chart(self):
        """Create a basic mock ScatterChart."""
        chart = MagicMock(spec=ScatterChart)
        chart.title = None
        chart.x_axis = MagicMock()
        chart.x_axis.title = None
        chart.x_axis.scaling = MagicMock()
        chart.x_axis.scaling.min = None
        chart.x_axis.scaling.max = None
        chart.y_axis = MagicMock()
        chart.y_axis.title = None
        chart.series = []
        return chart
    
    def test_scatter_chart_found(self, mock_scatter_chart):
        """Should award 3 points when XY scatter chart is found."""
        from graders.income_analysis.check_scatterplot import check_scatterplot
        
        ws = MagicMock()
        ws._charts = [mock_scatter_chart]
        
        chart_score, trendline_score, feedback = check_scatterplot(ws)
        
        # Should get 3 points just for having a scatter chart
        assert chart_score >= 3.0
        assert any(code == "IA_SCATTER_FOUND" for code, _ in feedback)


class TestCheckScatterplotTitle:
    """Tests for chart title (1 point)."""
    
    @pytest.fixture
    def mock_scatter_chart(self):
        """Create a mock ScatterChart."""
        chart = MagicMock(spec=ScatterChart)
        chart.title = None
        chart.x_axis = MagicMock()
        chart.x_axis.title = None
        chart.x_axis.scaling = MagicMock()
        chart.x_axis.scaling.min = None
        chart.x_axis.scaling.max = None
        chart.y_axis = MagicMock()
        chart.y_axis.title = None
        chart.series = []
        return chart
    
    def test_title_present_string(self, mock_scatter_chart):
        """Should award 1 point when chart has string title."""
        from graders.income_analysis.check_scatterplot import check_scatterplot
        
        mock_scatter_chart.title = "Income vs Experience"
        
        ws = MagicMock()
        ws._charts = [mock_scatter_chart]
        
        chart_score, trendline_score, feedback = check_scatterplot(ws)
        
        # 3 (chart) + 1 (title) = 4
        assert chart_score >= 4.0
        assert any(code == "IA_SCATTER_TITLE_PRESENT" for code, _ in feedback)
    
    def test_title_missing(self, mock_scatter_chart):
        """Should not award point when title is missing."""
        from graders.income_analysis.check_scatterplot import check_scatterplot
        
        mock_scatter_chart.title = None
        
        ws = MagicMock()
        ws._charts = [mock_scatter_chart]
        
        chart_score, trendline_score, feedback = check_scatterplot(ws)
        
        assert any(code == "IA_SCATTER_TITLE_MISSING" for code, _ in feedback)
    
    def test_title_empty_string(self, mock_scatter_chart):
        """Should not award point when title is empty string."""
        from graders.income_analysis.check_scatterplot import check_scatterplot
        
        mock_scatter_chart.title = "   "  # Whitespace only
        
        ws = MagicMock()
        ws._charts = [mock_scatter_chart]
        
        chart_score, trendline_score, feedback = check_scatterplot(ws)
        
        assert any(code == "IA_SCATTER_TITLE_MISSING" for code, _ in feedback)


class TestCheckScatterplotAxisLabels:
    """Tests for axis labels (1 point each)."""
    
    @pytest.fixture
    def mock_scatter_chart(self):
        """Create a mock ScatterChart."""
        chart = MagicMock(spec=ScatterChart)
        chart.title = None
        chart.x_axis = MagicMock()
        chart.x_axis.title = None
        chart.x_axis.scaling = MagicMock()
        chart.x_axis.scaling.min = None
        chart.x_axis.scaling.max = None
        chart.y_axis = MagicMock()
        chart.y_axis.title = None
        chart.series = []
        return chart
    
    def test_x_axis_label_present(self, mock_scatter_chart):
        """Should award 1 point when X-axis has label."""
        from graders.income_analysis.check_scatterplot import check_scatterplot
        
        mock_scatter_chart.x_axis.title = "Years of Experience"
        
        ws = MagicMock()
        ws._charts = [mock_scatter_chart]
        
        chart_score, trendline_score, feedback = check_scatterplot(ws)
        
        assert any(code == "IA_SCATTER_XLABEL_PRESENT" for code, _ in feedback)
    
    def test_x_axis_label_missing(self, mock_scatter_chart):
        """Should report missing X-axis label."""
        from graders.income_analysis.check_scatterplot import check_scatterplot
        
        mock_scatter_chart.x_axis.title = None
        
        ws = MagicMock()
        ws._charts = [mock_scatter_chart]
        
        chart_score, trendline_score, feedback = check_scatterplot(ws)
        
        assert any(code == "IA_SCATTER_XLABEL_MISSING" for code, _ in feedback)
    
    def test_y_axis_label_present(self, mock_scatter_chart):
        """Should award 1 point when Y-axis has label."""
        from graders.income_analysis.check_scatterplot import check_scatterplot
        
        mock_scatter_chart.y_axis.title = "Annual Income"
        
        ws = MagicMock()
        ws._charts = [mock_scatter_chart]
        
        chart_score, trendline_score, feedback = check_scatterplot(ws)
        
        assert any(code == "IA_SCATTER_YLABEL_PRESENT" for code, _ in feedback)
    
    def test_y_axis_label_missing(self, mock_scatter_chart):
        """Should report missing Y-axis label."""
        from graders.income_analysis.check_scatterplot import check_scatterplot
        
        mock_scatter_chart.y_axis.title = None
        
        ws = MagicMock()
        ws._charts = [mock_scatter_chart]
        
        chart_score, trendline_score, feedback = check_scatterplot(ws)
        
        assert any(code == "IA_SCATTER_YLABEL_MISSING" for code, _ in feedback)


class TestCheckScatterplotTrendline:
    """Tests for trendline (1 point)."""
    
    @pytest.fixture
    def mock_scatter_chart(self):
        """Create a mock ScatterChart."""
        chart = MagicMock(spec=ScatterChart)
        chart.title = None
        chart.x_axis = MagicMock()
        chart.x_axis.title = None
        chart.x_axis.scaling = MagicMock()
        chart.x_axis.scaling.min = None
        chart.x_axis.scaling.max = None
        chart.y_axis = MagicMock()
        chart.y_axis.title = None
        chart.series = []
        return chart
    
    def test_trendline_present(self, mock_scatter_chart):
        """Should award 1 point when series has trendline."""
        from graders.income_analysis.check_scatterplot import check_scatterplot
        
        # Create mock series with trendline
        series = MagicMock(spec=XYSeries)
        series.trendline = MagicMock()
        series.trendline.forward = None
        series.trendline.backward = None
        mock_scatter_chart.series = [series]
        
        ws = MagicMock()
        ws._charts = [mock_scatter_chart]
        
        chart_score, trendline_score, feedback = check_scatterplot(ws)
        
        assert any(code == "IA_SCATTER_TRENDLINE_PRESENT" for code, _ in feedback)
    
    def test_trendline_missing(self, mock_scatter_chart):
        """Should report missing trendline."""
        from graders.income_analysis.check_scatterplot import check_scatterplot
        
        # Create mock series without trendline
        series = MagicMock(spec=XYSeries)
        series.trendline = None
        mock_scatter_chart.series = [series]
        
        ws = MagicMock()
        ws._charts = [mock_scatter_chart]
        
        chart_score, trendline_score, feedback = check_scatterplot(ws)
        
        assert any(code == "IA_SCATTER_TRENDLINE_MISSING" for code, _ in feedback)
    
    def test_no_series(self, mock_scatter_chart):
        """Should report missing trendline when no series."""
        from graders.income_analysis.check_scatterplot import check_scatterplot
        
        mock_scatter_chart.series = []
        
        ws = MagicMock()
        ws._charts = [mock_scatter_chart]
        
        chart_score, trendline_score, feedback = check_scatterplot(ws)
        
        assert any(code == "IA_SCATTER_TRENDLINE_MISSING" for code, _ in feedback)


class TestCheckScatterplotExtension:
    """Tests for trendline extension (1 point)."""
    
    @pytest.fixture
    def mock_scatter_chart(self):
        """Create a mock ScatterChart with trendline."""
        chart = MagicMock(spec=ScatterChart)
        chart.title = None
        chart.x_axis = MagicMock()
        chart.x_axis.title = None
        chart.x_axis.scaling = MagicMock()
        chart.x_axis.scaling.min = None
        chart.x_axis.scaling.max = None
        chart.y_axis = MagicMock()
        chart.y_axis.title = None
        
        # Add series with trendline
        series = MagicMock(spec=XYSeries)
        series.trendline = MagicMock()
        series.trendline.forward = None
        series.trendline.backward = None
        chart.series = [series]
        
        return chart
    
    def test_extension_via_trendline_forward(self, mock_scatter_chart):
        """Should award point when trendline has forward extension."""
        from graders.income_analysis.check_scatterplot import check_scatterplot
        
        mock_scatter_chart.series[0].trendline.forward = 16  # Extends 16 years forward
        
        ws = MagicMock()
        ws._charts = [mock_scatter_chart]
        
        chart_score, trendline_score, feedback = check_scatterplot(ws)
        
        assert any(code == "IA_SCATTER_EXTENDED_CORRECT" for code, _ in feedback)
    
    def test_extension_via_axis_scaling(self, mock_scatter_chart):
        """Should award point when axis max is extended."""
        from graders.income_analysis.check_scatterplot import check_scatterplot
        
        mock_scatter_chart.x_axis.scaling.max = 24
        
        ws = MagicMock()
        ws._charts = [mock_scatter_chart]
        
        chart_score, trendline_score, feedback = check_scatterplot(ws)
        
        assert any(code == "IA_SCATTER_EXTENDED_CORRECT" for code, _ in feedback)
    
    def test_extension_missing(self, mock_scatter_chart):
        """Should report missing extension."""
        from graders.income_analysis.check_scatterplot import check_scatterplot
        
        # No forward extension and axis not extended
        mock_scatter_chart.series[0].trendline.forward = None
        mock_scatter_chart.x_axis.scaling.max = 8  # Only covers original data
        
        ws = MagicMock()
        ws._charts = [mock_scatter_chart]
        
        chart_score, trendline_score, feedback = check_scatterplot(ws)
        
        assert any(code == "IA_SCATTER_EXTENDED_MISSING" for code, _ in feedback)


class TestCheckScatterplotPerfectScore:
    """Tests for perfect score scenario."""
    
    def test_perfect_chart_all_criteria(self):
        """Should award 8 points for perfect chart."""
        from graders.income_analysis.check_scatterplot import check_scatterplot
        
        # Create perfect chart
        chart = MagicMock(spec=ScatterChart)
        chart.title = "Income vs Years of Experience"
        
        chart.x_axis = MagicMock()
        chart.x_axis.title = "Years of Experience"
        chart.x_axis.scaling = MagicMock()
        chart.x_axis.scaling.min = 0
        chart.x_axis.scaling.max = 24
        
        chart.y_axis = MagicMock()
        chart.y_axis.title = "Annual Income ($)"
        
        series = MagicMock(spec=XYSeries)
        series.trendline = MagicMock()
        series.trendline.forward = 16
        series.trendline.backward = None
        chart.series = [series]
        
        ws = MagicMock()
        ws._charts = [chart]
        
        chart_score, trendline_score, feedback = check_scatterplot(ws)
        
        # Should get full 8 points
        assert chart_score == 6.0 and trendline_score == 2.0
        
        # Should have all positive feedback codes
        codes = [code for code, _ in feedback]
        assert "IA_SCATTER_FOUND" in codes
        assert "IA_SCATTER_TITLE_PRESENT" in codes
        assert "IA_SCATTER_XLABEL_PRESENT" in codes
        assert "IA_SCATTER_YLABEL_PRESENT" in codes
        assert "IA_SCATTER_TRENDLINE_PRESENT" in codes
        assert "IA_SCATTER_EXTENDED_CORRECT" in codes


class TestCheckScatterplotFeedbackFormat:
    """Tests that feedback follows expected format."""
    
    def test_feedback_is_list_of_tuples(self):
        """Feedback should be list of (code, params) tuples."""
        from graders.income_analysis.check_scatterplot import check_scatterplot
        
        ws = MagicMock()
        ws._charts = []
        
        chart_score, trendline_score, feedback = check_scatterplot(ws)
        
        assert isinstance(feedback, list)
        for item in feedback:
            assert isinstance(item, tuple)
            assert len(item) == 2
            code, params = item
            assert isinstance(code, str)
            assert isinstance(params, dict)
    
    def test_all_codes_start_with_ia_scatter(self):
        """All feedback codes should start with IA_SCATTER_."""
        from graders.income_analysis.check_scatterplot import check_scatterplot
        
        # Test with no chart
        ws = MagicMock()
        ws._charts = []
        
        chart_score, trendline_score, feedback = check_scatterplot(ws)
        
        for code, _ in feedback:
            assert code.startswith("IA_SCATTER_"), f"Code '{code}' should start with 'IA_SCATTER_'"
