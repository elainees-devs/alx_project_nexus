from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Industry, Company
from .serializers import IndustrySerializer, CompanySerializer

class IndustryAPIView(APIView):
    def get(self, request):
        industries = Industry.objects.all()
        serializer = IndustrySerializer(industries, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = IndustrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def put(self, request, pk):
        try:
            industry = Industry.objects.get(pk=None)
        except Industry.DoesNotExist:
            return Response({"error": "Industry not found"}, status=404)
        
        serializer = IndustrySerializer(industry, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    def delete(self, request, pk):
        try:
            industry = Industry.objects.get(pk=None)
        except Industry.DoesNotExist:
            return Response({"error": "Industry not found"}, status=404)
        
        industry.delete()
        return Response(status=204)
    

class CompanyAPIVIEW(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        companies = Company.objects.all()
        serializer = CompanySerializer(companies, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def put(self, request, pk):
        try:
            company = Company.objects.get(pk=None)
        except Company.DoesNotExist:
            return Response({"error": "Company not found"}, status=404)
        
        serializer = CompanySerializer(company, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    def delete(self, request, pk):
        try:
            company = Company.objects.get(pk=None)
        except Company.DoesNotExist:
            return Response({"error": "Company not found"}, status=404)
        
        company.delete()
        return Response(status=204)
    
