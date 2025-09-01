#!/bin/bash

# Create folders
mkdir -p data/fixture_corpus/{news,blogs,reports}

# News (2 docs)
cat > data/fixture_corpus/news/news_001.txt << 'EOF'
The central bank raised interest rates today. Markets reacted with caution.
EOF
cat > data/fixture_corpus/news/news_002.txt << 'EOF'
Elections are scheduled next month as parties announce policy platforms.
EOF

# Blogs (2 docs)
cat > data/fixture_corpus/blogs/blog_001.txt << 'EOF'
I tried a new recipe today and documented each step with photos.
EOF
cat > data/fixture_corpus/blogs/blog_002.txt << 'EOF'
Traveling by train feels slower but reveals quiet landscapes and stories.
EOF

# Reports (2 docs)
cat > data/fixture_corpus/reports/report_001.txt << 'EOF'
The quarterly report outlines revenue growth and reduced operational costs.
EOF
cat > data/fixture_corpus/reports/report_002.txt << 'EOF'
The committee recommends additional audits to ensure compliance.
EOF
